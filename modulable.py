#!/usr/bin/env python3.4
# coding: utf-8

__version__ = '1.0'

__all__ = (
    'Plugin',
    'Modular',
    'modulable',
    'overridable',
    'alternative'
)

import os
import functools
from importlib.machinery import SourceFileLoader
from contextlib import contextmanager
from pathlib import Path
from collections import OrderedDict


class Plugin:
    """
    A module that can be injected in a modular class.
    """

    def __init__(self, name, path, module, on_load=None, on_unload=None):
        self.name = name
        self.path = path
        self.module = module

        self.on_load = on_load or (lambda: None)
        self.on_unload = on_unload or (lambda: None)

    @classmethod
    def load(cls, path):
        spath = str(path.resolve())
        name = os.path.basename(spath).split('.')[0]
        module = SourceFileLoader(name, spath).load_module()
        plugin = cls(name, path, module)

        try:
            on_load = getattr(module, 'on_load')
        except AttributeError:
            pass
        else:
            delattr(module, 'on_load')
            plugin.on_load = on_load

        try:
            on_unload = getattr(module, 'on_unload')
        except AttributeError:
            pass
        else:
            delattr(module, 'on_unload')
            plugin.on_unload = on_unload

        return plugin


class _ModularMeta(type):
    """
    A class that can load plugins.
    """

    def __new__(mcs, name, bases, attrs, virtual=False, plugin_directory='.'):
        return super().__new__(mcs, name, bases, attrs)

    def __init__(cls, name, bases, attrs, virtual=False, plugin_directory='.'):
        super().__init__(name, bases, attrs)

        # Use virtual = True if the class is meant to be derived
        cls.virtual = virtual

        if not virtual:
            cls.plugin_directory = Path(plugin_directory)
            cls.loaded_plugins = OrderedDict()
            cls.load_plugins()

    def __getattribute__(cls, name):
        try:
            val = super().__getattribute__('__dict__')[name]
        except KeyError:
            return super().__getattribute__(name)
        else:
            return val

    @contextmanager
    def plugin(cls, name):
        yield cls.load_plugin(name)
        cls.unload_plugin(name)

    def load_plugin_from_path(cls, path):
        """
        Loads a plugin given it's path.
        """

        plugin = Plugin.load(path)
        plugin.on_load()

        for attr, val in cls.__dict__.items():
            try:
                mod_fn = getattr(plugin.module, attr)
            except AttributeError:
                pass
            else:
                if isinstance(val, _ModulableMethod):
                    val.inject(mod_fn)
                elif isinstance(val, _OverridableMethod):
                    val.override(mod_fn)
                elif isinstance(val, _AlternativeMethod):
                    val.alternatively(mod_fn)

        cls.loaded_plugins[plugin.name] = plugin

        return plugin

    def load_plugin(cls, name):
        """
        Loads a plugin with a given name.
        """

        path = cls.plugin_directory / (name + '.py')
        return cls.load_plugin_from_path(path)


    def load_plugins(cls):
        """
        Loads every plugin from the plugin directory.
        """

        for path in cls.plugin_directory.glob('*.py'):
            cls.load_plugin_from_path(path)

    def unload_plugin(cls, name):
        """
        Unloads a plugin.
        """

        plugin = cls.loaded_plugins.pop(name)
        plugin.on_unload()

        for attr, val in plugin.module.__dict__.items():
            try:
                mth = getattr(cls, attr)
            except AttributeError:
                pass
            else:
                if isinstance(mth, modulable):
                    mth.fns.remove(val)
                elif isinstance(mth, overridable):
                    mth.overridden = None


class Modular(metaclass=_ModularMeta, virtual=True):
    """
    Modular class base class.
    """


class _WrappedMethod(functools.partialmethod):
    """
    A callable descriptor which handles method bounding.
    The objects conserves the informations of the provided function.
    """

    def __init__(self):
        super().__init__(self.__call__)

    def _make_unbound_method(self):
        mth = super()._make_unbound_method()
        functools.update_wrapper(mth, self.fn)
        return mth


class _ModulableMethod(_WrappedMethod):
    """
    A method that can have multiple implementations.
    """

    def __init__(self, fn, *fns):
        super().__init__()
        self.fn = fn
        self.fns = list(fns)
        functools.update_wrapper(self, fn)

    def __call__(self, obj, *args, **kwds):
        self.fn(obj, *args, **kwds)
        for fn in self.fns:
            fn(obj, *args, **kwds)

    def __repr__(self):
        return '<modulable method {self.__qualname__} at {id}>'.format(self=self, id=hex(id(self)))

    def inject(self, fn):
        self.fns.append(fn)


def modulable(fn):
    """
    Decorator for modulable methods.
    """

    return _ModulableMethod(fn)


class _OverridableMethod(_WrappedMethod):
    """
    A method which can be overriden in a plugin, but has only one implementation.
    """

    def __init__(self, fn):
        super().__init__()
        self.fn = fn
        self.overriden = None
        functools.update_wrapper(self, fn)

    def __call__(self, obj, *args, **kwds):
        if self.overriden is not None:
            return self.overriden(obj, *args, **kwds)
        else:
            return self.fn(obj, *args, **kwds)

    def __repr__(self):
        return '<overridable method {self.__qualname__} at {id}>'.format(self=self, id=hex(id(self)))

    def override(self, fn):
        self.overriden = fn


def overridable(fn):
    """
    Decorator for overridable methods.
    """

    return _OverridableMethod(fn)


class _AlternativeMethod(_WrappedMethod):
    """
    A method that tests every function alternative until it finds one that
    doesn't raise an exception.
    """

    def __init__(self, fn, exc_types):
        super().__init__()
        self.fn = fn
        self.alternatives = []
        self.exc_types = exc_types

    def __call__(self, obj, *args, **kwds):
        for alt in self.alternatives:
            try:
                return alt(obj, *args, **kwds)
            except Exception as exc:
                if isinstance(exc, self.exc_types):
                    pass
                elif isinstance(exc, type) and issubclass(exc, self.exc_types):
                    pass
                else:
                    raise

        return self.fn(obj, *args, **kwds)

    def __repr__(self):
        return '<alternative method {self.__qualname__} at {id}>'.format(self=self, id=hex(id(self)))

    def alternatively(self, fn):
        self.alternatives.append(fn)


def alternative(*exc_types):
    """
    Decorator for alternative methods.
    """

    return functools.partial(_AlternativeMethod, exc_types=exc_types)

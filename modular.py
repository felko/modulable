#!/usr/bin/env python3.4
# coding: utf-8

__all__ = (
    'Plugin',
    'Modular',
    'modulable',
    'overridable'
)

import os
import functools
from importlib.machinery import SourceFileLoader
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
                if isinstance(val, modulable):
                    val.inject(mod_fn)
                elif isinstance(val, overridable):
                    val.override(mod_fn)

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


class _WrappedMethodDecorator(functools.partialmethod):
    """
    A callable descriptor which handles method bounding.
    The objects conserves the informations of the provided function.
    """

    def _make_unbound_method(self):
        mth = super()._make_unbound_method()
        functools.update_wrapper(mth, self.fn)
        return mth


class modulable(_WrappedMethodDecorator):
    """
    A method that can have multiple implementations.
    """

    def __init__(self, fn, *fns):
        super().__init__(self.__call__)
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


class overridable(_WrappedMethodDecorator):
    """
    A method which can be overriden in a plugin, but has only one implementation.
    """

    def __init__(self, fn):
        self.fn = fn
        self.overriden = None
        functools.update_wrapper(self, fn)

    def __call__(self, obj, *args, **kwds):
        if self.overriden:
            self.overriden(obj, *args, **kwds)
        else:
            self.fn(obj, *args, **kwds)

    def __repr__(self):
        return '<overridable method {self.__qualname__} at {id}>'.format(self=self, id=hex(id(self)))

    def inject(self, fn):
        self.overriden = fn

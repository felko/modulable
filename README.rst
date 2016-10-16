modulable.py
============

|PyPI version| |License| |Supported Python| |Format| |Downloads|

``modular.py`` is a small library that helps you write a modular and
maintainable codebase.

The library works with class: the loaded plug-ins are "injected" in
the given class. You can specify the way of injection, either by stacking
functions, with the ``modulable`` decorator, by overloading the base method, with
the ``overridable`` decorator, and finally with the ``alternative`` decorator,
which runs every function until it finds one that doesn't raise an exception.

Those decorators conserve the original method's informations, such as name,
module, docstring, and annotations.


Example
-------

Let's say you want to build a modular shell, where the users can implement their
own commands and prompt for example.

.. code:: python3

    from modular import *

    class Shell(Modular, plugin_directory='plugins'):

This declares a modular class, whose plug-ins are in the ``plugins`` directory
relative to the current working directory.

The library will load every plug-in (must be a .py file) in that directory when
the class is instantiated.

It is convenient to declare a ``init`` method, called within the real
``__init__`` constructor, to allow users to initialize their plug-in specific
attributes:

.. code:: python3

    def __init__(self, *args, **kwds):
        self.init(*args, **kwds)

    @modulable
    def init(self, *args, **kwds):
        self.running = False

Here, we decorate the ``init`` method with ``modulable``. That means every
plug-ins' implementations of the ``init`` method will be executed with the given
arguments.

Next, we want a function that is executed between every command, and, say, a
method that returns the shell prompt:

.. code:: python3

    @modulable
    def update(self):
        pass

    @overridable
    def prompt(self):
        return '> '

This time, we use the ``overridable`` decorator. This decorator uses the last
implementation of ``prompt`` loaded.

Lastly, we want a function that reacts on user input. What we want here is to
run every implementation until one works (i.e. doesn't raise an error). To do
that, you can use the ``alternative`` decorator which takes an exception type
and calls every implementation one-by-one until one doesn't raise an error of
this type:

.. code:: python3

    @alternative(ValueError)
    def react(self, i):
        if i:
            print('Unrecognized command:', repr(i))

We provide a default case here, if there isn't any implementation working.

Finally, we define some non-modulable methods to make the whole thing works:

.. code:: python3

    def run(self):
        self.running = True

        while self.running:
            i = input(self.prompt())
            self.react(i)
            self.update()

For instance, our shell doesn't implement any plug-in. Just for the example,
we'll implement a ``quit`` plug-in, which stops the shell when the user types in
``quit``, a ``greet`` plug-in, and finally we'll customize our prompt.

The implementation of the ``quit`` command is pretty straight-forward:

.. code:: python3

    def react(self, i):
        if i == 'quit':
            self.running = False
        else:
            raise ValueError

By raising ``ValueError``, we delegate the input processing to the next
implementation of ``react``.

The ``greet`` plug-in does the same, with a bit more complex parsing:

.. code:: python3

    def react(self, i):
        lexemes = i.split()

        try:
            if lexemes[0] == 'greet':
                print('Hey', lexemes[1], '!')
            else:
                raise ValueError
        except IndexError:
            raise ValueError

Finally, lets define a prompt that displays the command count:

.. code:: python3

    def init(self, *args, **kwds):
        self.command_count = 0

    def update(self):
        self.command_count += 1

    def prompt(self):
        return '[{}]: '.format(self.command_count)

The plug-ins must be contained in the specified plug-in directory in the class
declaration, here, ``plugins``. You should have a similar directory tree:

::

    .
    ├── plugins
    │   ├── command_count_prompt.py
    │   ├── greet.py
    │   └── quit.py
    └── shell.py

To use this class, simply instantiate a ``Shell`` object and call its ``run``
method:

.. code:: python3

    sh = Shell()
    sh.run()

Here's what it does:

::

    [0]:
    [1]:
    [2]: greet Jonathan
    Hey Jonathan !
    [3]:
    [4]:
    [5]: unknown command
    Unrecognized command: 'unknown command'
    [6]:
    [7]: quit

You can see the complete code in the `example directory`_.


Advanced use
------------

You can temporarily load a plug-in with the ``plugin`` context manager:

.. code:: python3

    with Shell.plugin('greet'):
        sh.run()

You can also check the loaded plug-ins by typing ``Shell.loaded_plugins``.

Finally, there is an optional ``virtual`` keyword argument at class definition.
``virtual`` is set to ``False`` by default, but if set to ``True``, the class
will not load the plug-ins automatically:

.. code:: python3

    class AbstractShell(Modular, plugins='plugins', virtual=True):
        ...


Installation
------------

* Via `pip`_:

.. code:: bash

    $ pip install modulable


And, if you're on Linux, and face a permission error, make sure to
run ``sudo`` with the ``-H`` option:

.. code:: bash

    $ sudo -H pip install modulable

* Via `git`_:

.. code:: bash

    $ git clone http://github.com/felko/modulable.git
    $ cd modulable
    $ sudo -H python3.4 setup.py install

Or, if you're on Windows:

.. code:: bash

    $ git clone http://github.com/felko/modulable.git
    $ cd modulable
    $ py -3.4 setup.py install

If you don't have `git`_, you can download the zip file `here <https://github.com/felko/modulable/archive/master.zip>`_.


Links
-----

- GitHub: http://github.com/felko/modulable
- Issue Tracker: http://github.com/feko/modulable/issues
- PyPI: http://pypi.python.org/pypi/modulable
- Download: http://pypi.python.org/pypi/modulable#downloads


License
-------

``modulable`` is distributed under the `MIT license`_.


.. _pip: http://pip.readthedocs.io/
.. _example directory: https://github.com/felko/modulable/tree/master/examples
.. _MIT license: http://opensource.org/licenses/MIT
.. _git: https://git-scm.com/


.. |PyPI version| image:: https://img.shields.io/pypi/v/modulable.svg
    :target: https://pypi.python.org/pypi/modulable
    :alt: Latest PyPI Version
.. |License| image:: https://img.shields.io/pypi/l/modulable.svg
    :target: https://pypi.python.org/pypi/modulable
    :alt: License
.. |Supported Python| image:: https://img.shields.io/pypi/pyversions/modulable.svg
    :target: https://pypi.python.org/pypi/modulable
    :alt: Supported Python Versions
.. |Format| image:: https://img.shields.io/pypi/format/modulable.svg
    :target: https://pypi.python.org/pypi/modulable
    :alt: Format
.. |Downloads| image:: https://img.shields.io/pypi/dm/modulable.svg
    :target: https://pypi.python.org/pypi/modulable
    :alt: Downloads

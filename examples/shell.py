#!/usr/bin/env python3.4
# coding: utf-8

import os

from modulable import *

# we want to execute this file from the project's root directory because this
# is where modular.py is located.
os.chdir('examples')

# Declares a modular class, whose plugins are in the `plugins` directory,
# relative to the current path
class Shell(Modular, plugin_directory='plugins'):
    """
    A modular shell.
    """

    def __init__(self, *args, **kwds):
        self.init(*args, **kwds)

    # Convenience: declare a init method which will be overloaded if needed
    # We don't want the real __init__ function to be overloaded
    # We choose the modulable decorator because every plugin should be able
    # to initialize some base attributes
    @modulable
    def init(self, *args, **kwds):
        """
        Initialize the shell.
        """

        self.running = False


    # modulable, again, because we want every plugin to be able to run code
    # between every command.
    @modulable
    def update(self):
        """
        Updates the current shell.
        """

        pass

    # We use overridable this time because there can be only one prompt.
    @overridable
    def prompt(self):
        """
        Returns the command prompt.
        """

        return '> '

    # We declare the method with the alternative decorator because every plugin
    # will potentially fail if the given input is not considered as valid.
    # In case of failure for every alternative, this is the code that will be
    # executed.
    @alternative(ValueError)
    def react(self, i):
        """
        Reacts on a given input.
        """

        # empty input is skipped
        if i:
            print('Unrecognized command:', repr(i))

    def run(self):
        self.running = True

        while self.running:
            i = input(self.prompt())
            self.react(i)
            self.update()


if __name__ == '__main__':
    sh = Shell()
    sh.run()

#!/usr/bin/env python3.4
# coding: utf-8

import os

from modular import *

os.chdir('examples')

class Interface(Modular, plugin_directory='plugins'):
    @modulable
    def init(self, *args, **kwds):
        self.frame = 0
        self.running = False

    @modulable
    def update(self):
        """
        Updates caca
        """

        print('=== Frame:', self.frame, '===')
        self.frame += 1

    def run(self, *args, **kwds):
        self.init(*args, **kwds)

        self.running = True

        while self.running:
            self.update()

if __name__ == '__main__':
    i = Interface()
    i.run()
    Interface.unload_plugin('it_works')
    i.run()

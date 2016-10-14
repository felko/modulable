#!/usr/bin/env python3.4
# coding: utf-8

def init(self, *args, **kwds):
    print('starting')

def update(self):
    if self.frame > 10:
        self.running = False

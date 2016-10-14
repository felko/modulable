#!/usr/bin/env python3.4
# coding: utf-8

def on_load():
    print('Loading stop_at_10...')

def init(self, *args, **kwds):
    print('starting')

def update(self):
    if self.frame > 10:
        self.running = False

#!/usr/bin/env python3.4
# coding: utf-8

def init(self, *args, **kwds):
    self.command_count = 0

def update(self):
    self.command_count += 1
    
def prompt(self):
    return '[{}]: '.format(self.command_count)

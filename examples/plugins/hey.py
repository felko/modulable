#!/usr/bin/env python3.4
# coding: utf-8

def react(self, i):
    lexemes = i.split()

    try:
        if lexemes[0] == 'hey':
            print('Hey', lexemes[1], '!')
        else:
            raise ValueError
    except IndexError:
        raise ValueError

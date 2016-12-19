# -*- coding: utf-8 -*-
from .printer import PrintTemplate


class DummyPrinter(object):

    def __init__(self):
        return
    
    def writeln(self, s=None):
        print(s)

    def writelnright(self, s=None):
        self.writeln(s)

    def writelncenter(self, s=None):
        self.writeln(s)

    def write(self, s=None):
        self.writeln(s)

    def writeright(self, s=None):
        self.writeln(s)

    def writecenter(self, s=None):
        self.writeln(s)

    def writeln_with_size(self, s=None, w=0, h=0, textpos='left'):
        self.writeln(s)
        
    def close(self):
        return
        


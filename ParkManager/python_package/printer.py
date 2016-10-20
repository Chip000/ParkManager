# -*- coding: utf-8 -*-
from configparser import ConfigParser
from epson_printer.epsonprinter import EpsonPrinter


class Printer(object):
    def __init__(self):
        self.vendor = 0x04b8
        self.product = 0x0e03
        try:
            self.prnt = EpsonPrinter(self.vendor, self.product)
        except ValueError:
            raise

    def writeln(self, s=None):
        self.prnt.set_text_size(0, 0)
        self.prnt.left_justified()
        self.prnt.print_text(bytes(s, encoding='utf-8'))
        self.prnt.linefeed()

    def writelnright(self, s=None):
        self.prnt.set_text_size(0, 0)
        self.prnt.right_justified()
        self.prnt.print_text(bytes(s, encoding='utf-8'))
        self.prnt.linefeed()
        self.prnt.left_justified()

    def writelncenter(self, s=None):
        self.prnt.set_text_size(0, 0)
        self.prnt.center()
        self.prnt.print_text(bytes(s, encoding='utf-8'))
        self.prnt.linefeed()
        self.prnt.left_justified()

    def write(self, s=None):
        self.prnt.set_text_size(0, 0)
        self.prnt.left_justified()
        self.prnt.print_text(bytes(s, encoding='utf-8'))

    def writeright(self, s=None):
        self.prnt.set_text_size(0, 0)
        self.prnt.right_justified()
        self.prnt.print_text(bytes(s, encoding='utf-8'))
        self.prnt.left_justified()

    def writecenter(self, s=None):
        self.prnt.set_text_size(0, 0)
        self.prnt.center()
        self.prnt.print_text(bytes(s, encoding='utf-8'))
        self.prnt.left_justified()

    def writeln_with_size(self, s=None, w=0, h=0, textpos='left'):
        self.prnt.set_text_size(w, h)
        if textpos == 'left':
            self.prnt.left_justified()
            self.prnt.print_text(bytes(s, encoding='utf-8'))
        elif textpos == 'right':
            self.prnt.right_justified()
            self.prnt.print_text(bytes(s, encoding='utf-8'))
        elif textpos == 'center':
            self.prnt.center()
            self.prnt.print_text(bytes(s, encoding='utf-8'))
        else:
            raise ValueError('left, right or center')

        if not isinstance(w, int) or not isinstance(h, int):
            raise TypeError('width and height must be integer')

        self.prnt.linefeed()
        self.prnt.set_text_size(0, 0)
        self.prnt.left_justified()
        
    def close(self):
        self.prnt.linefeed(5)
        self.prnt.cut()
        
        
class PrintTemplate(object):
    def __init__(self, cfile=None):
        self.cfile = cfile
        self.config = ConfigParser()

        try:
            self.config.read_file(open(self.cfile))
        except:
            raise

        self.separator = "-" * 48
        
    def header(self):
        line = (self.separator,
                self.config['Dados']['nome'],
                self.config['Dados']['endereco'],
                self.config['Dados']['cidade-estado'],
                self.config['Dados']['cnpj'],
                self.separator)
        return line
    
    def footer(self):
        line = [self.separator]

        if len(self.config['Dados']['obs']) >= 48:
            obs = self.config['Dados']['obs'].split(" ")
            obsline = ""
            for word in obs:
                if len(obsline) + len(word) < 48:
                    obsline = " ".join((obsline, word))
                else:
                    line.append(obsline)
                    obsline = word
            line.append(obsline)
        else:
            line.append(self.config['Dados']['obs'])

        line.append(self.separator)
        
        return line

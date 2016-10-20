#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from PyQt5 import QtWidgets
from python_package.mainwindowex import MainWindowEx
from python_package.ui.parkmanager_rc import *

rootdir = os.getcwd()
cfgfile = os.path.join(rootdir, "settings.cfg")

if __name__ == "__main__":
    # verify if cfgfile exists
    try:
        with open(cfgfile, 'r') as f:
            f.readline()
    except IOError:
        print(u"Arquivo não existe.")
        f = open(cfgfile, 'w')
        f.close()
        print(u"Criado.")
    
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindowEx(cfgfile=cfgfile)
    mainWindow.showMaximized()
    sys.exit(app.exec_())

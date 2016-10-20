# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSignal, QObject


class Communicate(QObject):
    signal = pyqtSignal()

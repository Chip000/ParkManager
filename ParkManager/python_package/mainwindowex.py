# -*- coding: utf-8 -*-
from .ui.mainwindow import Ui_MainWindow
from .entradaex import EntradaEx
from .pagtoex import PagtoEx
from .configuracaoex import ConfiguracoesEx
from .relatorioex import RelatorioEx
from .communicate import Communicate
from .db import DB
from .printer import Printer
from .dummyprinter import DummyPrinter
from configparser import ConfigParser, NoSectionError
from PyQt5 import QtWidgets, QtCore
import os


class MainWindowEx(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, cfgfile=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.cfgfile = cfgfile

        # Setting mdiArea as central widget
        self.ui.mdiArea.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.ui.mdiArea.setViewMode(QtWidgets.QMdiArea.SubWindowView)
        self.setCentralWidget(self.ui.mdiArea)

        self.debug = True
        # Impressora
        try:
            self.printer = Printer()
        except ValueError:
            if not self.debug:
                QtWidgets.QMessageBox.critical(self, "Sem Impressora.",
                                               ("Impressora não "
                                                "encontrada. "
                                                "Verifique a conexão e "
                                                "inicie novamente"))
                raise
            else:
                self.printer = DummyPrinter()

        # Controle para abertura de uma janela
        self.entr = False
        self.cfg = False
        self.pagt = False
        self.rel = False
        
        # Verificando se as configuracoes contem todas info
        config = ConfigParser()
        config.read_file(open(self.cfgfile))
        try:
            if len(config.options('Dados')) < 6:
                self.on_actionDados_triggered()
                return
        except NoSectionError as err:
            self.on_actionDados_triggered()
            return

        try:
            if len(config.options('Valores')) < 4:
                self.on_actionValores_triggered()
                return
        except NoSectionError as err:
            self.on_actionValores_triggered()
            return

    def msgBox(self, text=None):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(u"Informação")
        msg.exec_()

    @QtCore.pyqtSlot(bool)
    def on_actionEntrada_triggered(self):
        if not self.entr:
            self.entr = True
            self.entsignal = Communicate()
            widget = EntradaEx(csignal=self.entsignal, cfgfile=self.cfgfile,
                               printer=self.printer)
            self.subwin = QtWidgets.QMdiSubWindow()
            self.subwin.setWidget(widget)
            self.subwin.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.ui.mdiArea.addSubWindow(self.subwin)
            self.subwin.show()
            self.entsignal.signal.connect(self.entrOpen)
        else:
            self.msgBox(u"Instância em execução.")

    def entrOpen(self):
        self.ui.mdiArea.closeActiveSubWindow()
        self.entr = False

    @QtCore.pyqtSlot(bool)
    def on_actionPagto_triggered(self):
        if not self.pagt:
            self.pagt = True
            self.pagtsignal = Communicate()
            widget = PagtoEx(csignal=self.pagtsignal, cfgfile=self.cfgfile,
                             printer=self.printer)
            self.subwin = QtWidgets.QMdiSubWindow()
            self.subwin.setWidget(widget)
            self.subwin.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.ui.mdiArea.addSubWindow(self.subwin)
            self.subwin.show()
            self.pagtsignal.signal.connect(self.pagtOpen)
        else:
            self.msgBox(u"Instância em execução.")

    def pagtOpen(self):
        self.ui.mdiArea.closeActiveSubWindow()
        self.pagt = False
        
    @QtCore.pyqtSlot(bool)
    def on_actionDados_triggered(self):
        if not self.cfg:
            self.cfg = True
            self.cfgsignal = Communicate()
            widget = ConfiguracoesEx(index="dados", csignal=self.cfgsignal,
                                     cfgfile=self.cfgfile)
            self.subwin = QtWidgets.QMdiSubWindow()
            self.subwin.setWidget(widget)
            self.subwin.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.subwin.setMinimumWidth(widget.minimumWidth()+15)
            self.subwin.setMaximumWidth(widget.maximumWidth()+15)
            self.ui.mdiArea.addSubWindow(self.subwin)
            self.subwin.show()
            self.cfgsignal.signal.connect(self.cfgOpen)
        else:
            self.msgBox(u"Instância em execução.")

    @QtCore.pyqtSlot(bool)
    def on_actionValores_triggered(self):
        if not self.cfg:
            self.cfg = True
            self.cfgsignal = Communicate()
            widget = ConfiguracoesEx(index="valores", csignal=self.cfgsignal,
                                     cfgfile=self.cfgfile)
            self.subwin = QtWidgets.QMdiSubWindow()
            self.subwin.setWidget(widget)
            self.subwin.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.subwin.setMinimumWidth(widget.minimumWidth()+15)
            self.subwin.setMaximumWidth(widget.maximumWidth()+15)
            self.ui.mdiArea.addSubWindow(self.subwin)
            self.subwin.show()
            self.cfgsignal.signal.connect(self.cfgOpen)
        else:
            self.msgBox(u"Instância em execução.")

    def cfgOpen(self):
        self.ui.mdiArea.closeActiveSubWindow()
        self.cfg = False

    @QtCore.pyqtSlot(bool)
    def on_actionRelatorio_triggered(self):
        if not self.rel:
            self.rel = True
            self.relsignal = Communicate()
            widget = RelatorioEx(csignal=self.relsignal, cfgfile=self.cfgfile)
            self.subwin = QtWidgets.QMdiSubWindow()
            self.subwin.setWidget(widget)
            self.subwin.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.ui.mdiArea.addSubWindow(self.subwin)
            self.subwin.show()
            self.relsignal.signal.connect(self.relOpen)
        else:
            self.msgBox(u"Instância em execução.")

    def relOpen(self):
        self.ui.mdiArea.closeActiveSubWindow()
        self.rel = False
        
    @QtCore.pyqtSlot(bool)
    def on_actionBackup_triggered(self):
        self.msgBox(("Preparando para realizar o backup."
                     " Aperte OK para continuar"))

        root = os.path.abspath('.')
        backupdir = os.path.join(root, "backups")
        
        db = DB()
        try:
            db.backup(path=backupdir)
        except ValueError:
            self.msgBox("Backup não realizado. Diretório Inválido.")
            
        db.close()
        
        self.msgBox(("Backup realizado."
                     " Aperte OK para continuar"))
        
    @QtCore.pyqtSlot(bool)
    def on_actionCascada_triggered(self):
        self.ui.mdiArea.cascadeSubWindows()

    @QtCore.pyqtSlot(bool)
    def on_actionTiled_triggered(self):
        self.ui.mdiArea.tileSubWindows()

    @QtCore.pyqtSlot(bool)
    def on_actionFecharTodos_triggered(self):
        self.ui.mdiArea.closeAllSubWindows()
        self.entr = False
        self.cfg = False
        self.pagt = False
        self.rel = False

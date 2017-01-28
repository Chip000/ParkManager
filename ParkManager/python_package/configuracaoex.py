# -*- coding: utf-8 -*-
from .ui.configuracao import Ui_Configuracoes
from .communicate import Communicate
from PyQt5 import QtWidgets, QtCore
from configparser import ConfigParser


class ConfiguracoesEx(QtWidgets.QWidget, Ui_Configuracoes):
    tabs = {"dados": 0, "valores": 1}

    def __init__(self, parent=None, index="dados", csignal=None, cfgfile=None):
        super().__init__(parent)

        if csignal is None:
            self.csignal = Communicate()
        else:
            self.csignal = csignal

        self.ui = Ui_Configuracoes()
        self.ui.setupUi(self)
        self.ui.tabWidget.setCurrentIndex(self.tabs[index])
        self.cfgfile = cfgfile

        config = ConfigParser()
        config.read_file(open(self.cfgfile))

        try:
            self.ui.nomeLE.setText(config['Dados']['nome'])
            self.ui.enderecoLE.setText(config['Dados']['endereco'])
            self.ui.cidadeLE.setText(config['Dados']['cidade-estado'])
            self.ui.cnpjLE.setText(config['Dados']['cnpj'])
            self.ui.telefoneLE.setText(config['Dados']['telefone'])
            self.ui.obsPTE.setPlainText(config['Dados']['obs'])
        except KeyError as err:
            if err.args[0] != "Dados":
                self.msgBox(u"Seção 'Dados' incompleta.")
            else:
                self.msgBox(u"Seção 'Dados' não existe.")
        try:
            self.ui.maxVagasLE.setText(config['Valores']['vagas'])
            self.ui.meiaLE.setText(config['Valores']['meia'])
            self.ui.horaLE.setText(config['Valores']['hora'])
            self.ui.demaisLE.setText(config['Valores']['demais'])
            self.ui.diariaLE.setText(config['Valores']['diaria'])
            self.ui.mensalLE.setText(config['Valores']['mensal'])
        except KeyError as err:
            if err.args[0] != "Valores":
                self.msgBox(u"Seção 'Valores' incompleta.")
            else:
                self.msgBox(u"Seção 'Valores' não existe.")

    def msgBox(self, text=None):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(u"Informação")
        msg.exec_()

    @QtCore.pyqtSlot(bool)
    def on_fecharButton_clicked(self):
        self.csignal.signal.emit()

    def closeEvent(self, event):
        self.csignal.signal.emit()

    @QtCore.pyqtSlot(bool)
    def on_salvarButton_clicked(self):
        config = ConfigParser()
        config.read_file(open(self.cfgfile))
        formindex = self.ui.tabWidget.currentIndex()
        form = self.ui
            
        if formindex == 0:
            # Dados
            config['Dados'] = {'nome': form.nomeLE.text(),
                               'endereco': form.enderecoLE.text(),
                               'cidade-estado': form.cidadeLE.text(),
                               'cnpj': form.cnpjLE.text(),
                               'telefone': form.telefoneLE.text(),
                               'obs': form.obsPTE.toPlainText()}
        elif formindex == 1:
            # Valores
            config['Valores'] = {'vagas': form.maxVagasLE.text(),
                                 'meia': form.meiaLE.text(),
                                 'hora': form.horaLE.text(),
                                 'demais': form.demaisLE.text(),
                                 'diaria': form.diariaLE.text(),
                                 'mensal': form.mensalLE.text()}

        # Salvando as configurações no arquivo
        with open(self.cfgfile, 'w') as cfile:
            config.write(cfile)

        # Aviso da gravação
        self.msgBox(u"Configuração Gravada com Sucesso!")

# -*- coding: utf-8 -*-
from .ui.entrada import Ui_Entrada
from .communicate import Communicate
from .db import DB
from .printer import Printer, PrintTemplate
from PyQt5 import QtWidgets, QtCore
import string


class EntradaEx(QtWidgets.QWidget, Ui_Entrada):
    addquery = ("INSERT INTO entrada (dia, hora, placa, marca, modelo, cor) "
                "VALUES (%(dia)s, %(hora)s, %(placa)s,"
                " %(marca)s, %(modelo)s, %(cor)s)")
    searchquery = ("SELECT pagto.id, pagto.ent_id, entrada.placa "
                   "FROM pagto, entrada WHERE entrada.placa = %(placa)s "
                   "AND pagto.id = entrada.id")

    def __init__(self, parent=None, csignal=None, cfgfile=None,
                 printer=None):
        super().__init__(parent)
        
        if csignal is None:
            self.csignal = Communicate()
        else:
            self.csignal = csignal

        self.printer = printer
            
        self.ui = Ui_Entrada()
        self.ui.setupUi(self)
        self.cfgfile = cfgfile

        self.timerdate = QtCore.QTimer(self)
        self.timerdate.timeout.connect(self.showDate)
        self.timerdate.start(1000)
        self.showDate()
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.showTime)
        self.timer.start(1000)
        self.showTime()

        self.ui.placaLE.setFocus()

    def msgBox(self, text=None):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(u"Informação")
        msg.exec_()

    def timedMsgBox(self, text=None):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(u"Informação")
        timer = QtCore.QTimer(self)
        timer.timeout.connect(msg.close)
        timer.start(5000)
        msg.exec_()
        
    def showTime(self):
        time = QtCore.QTime.currentTime()
        text = time.toString("HH:mm:ss")
        self.ui.horasLE.setText(text)
        
    def showDate(self):
        date = QtCore.QDate.currentDate()
        text = date.toString("dd/MM/yyyy")
        self.ui.diaLE.setText(text)
        
    @QtCore.pyqtSlot(bool)
    def on_fecharButton_clicked(self):
        self.csignal.signal.emit()

    def closeEvent(self, event):
        self.csignal.signal.emit()

    @QtCore.pyqtSlot(bool)
    def on_modificarCkB_clicked(self, status):
        if status:
            self.ui.diaLE.setFocusPolicy(QtCore.Qt.StrongFocus)
            self.ui.diaLE.setReadOnly(False)
            self.timerdate.stop()
            self.ui.horasLE.setFocusPolicy(QtCore.Qt.StrongFocus)
            self.ui.horasLE.setReadOnly(False)
            self.timer.stop()
        else:
            self.ui.diaLE.setFocusPolicy(QtCore.Qt.NoFocus)
            self.ui.diaLE.setReadOnly(True)
            self.timerdate.start(1000)
            self.ui.horasLE.setFocusPolicy(QtCore.Qt.NoFocus)
            self.ui.horasLE.setReadOnly(True)
            self.timer.start(1000)
            
    @QtCore.pyqtSlot(bool)
    def on_novoButton_clicked(self):
        self.ui.placaLE.clear()
        self.ui.marcaLE.clear()
        self.ui.modeloLE.clear()
        self.ui.corLE.clear()
        self.ui.modificarCkB.setCheckState(QtCore.Qt.Unchecked)
        self.showDate()
        self.showTime()
        self.timer.start(1000)

    @QtCore.pyqtSlot(bool)
    def on_imprimirButton_clicked(self):
        # dia formato dia/mes/ano para ano-mes-dia
        dia = QtCore.QDate.fromString(self.ui.diaLE.text(), "dd/MM/yyyy")
        
        values = {'dia': dia.toString("yyyy-MM-dd"),
                  'hora': self.ui.horasLE.text(),
                  'placa': self.ui.placaLE.text().upper(),
                  'marca': self.ui.marcaLE.text().upper(),
                  'modelo': self.ui.modeloLE.text().upper(),
                  'cor': self.ui.corLE.text().upper()}
        
        # validando as variaveis
        if len(values['dia']) < 10 or len(values['hora']) < 8 or \
           len(values['placa']) < 7 or not values['marca'] or \
           not values['modelo'] or not values['cor']:
            self.msgBox((u"Preenchimento incorreto. "
                         u"Todos campos são obrigatórios."))
            return

        for ch in values['placa'][:3].upper():
            if ch not in string.ascii_uppercase:
                self.msgBox(u"Placa Inválida.")
                return
        for ch in values['placa'][3:].upper():
            if ch not in string.digits:
                self.msgBox(u"Placa Inválida.")
                return
        
        # commit no bd
        db = DB()
        res = db.fetchone(self.searchquery, values)
        if not res:
            values['ticket'] = db.insert(self.addquery, values)
        else:
            values['ticket'] = res[1]
        db.close()

        # imprimir
        template = PrintTemplate(self.cfgfile)
        if self.printer is None:
            ptr = Printer()
        else:
            ptr = self.printer

        # cabecalho
        for line in template.header():
            ptr.writelncenter(line)

        # No. ticket
        ptr.writeln("")
        line = "Ticket: {0:0>10}".format(values['ticket'])

        try:
            ptr.writeln_with_size(line, 1, 1, 'center')
        except TypeError as err:
            self.msgBox(("Aconteceu um erro com o tamanho da fonte.\n"
                         "Resumindo impressão normalmente.\n"
                         " Erro: {}.").format(err))
            ptr.writelncenter(line)
        except ValueError as err:
            self.msgBox(("Aconteceu um erro com a formatação do texto.\n"
                         "Resumindo impressão normalmente.\n"
                         " Erro: {}.").format(err))
            ptr.writelncenter(line)
            
        # data e Hora de entrada
        ptr.writeln("")
        ptr.writeln("Data Entrada: "+dia.toString("dd/MM/yyyy"))
        ptr.writeln("Hora Entrada: "+values['hora'])
        ptr.writeln("")
        
        # marca, modelo e cor
        line = values['marca'] + " " + values['modelo'] + " " + values['cor']
        if len(line) < 48:
            ptr.writelncenter(line)
        else:
            ptr.writeln("Marca : "+values['marca'])
            ptr.writeln("Modelo: "+values['modelo'])
            ptr.writeln("Cor   : "+values['cor'])

        # placa
        ptr.writeln("")
        line = "Placa: "+values['placa']

        try:
            ptr.writeln_with_size(line, 1, 1, 'center')
        except TypeError as err:
            self.msgBox(("Aconteceu um erro com o tamanho da fonte.\n"
                         "Resumindo impressão normalmente.\n"
                         " Erro: {}.").format(err))
            ptr.writelncenter(line)
        except ValueError as err:
            self.msgBox(("Aconteceu um erro com a formatação do texto.\n"
                         "Resumindo impressão normalmente.\n"
                         " Erro: {}.").format(err))
            ptr.writelncenter(line)

        ptr.writeln("")
        for line in template.footer():
            ptr.writelncenter(line)
        
        ptr.close()
        self.timedMsgBox(("Impressão finalizada.\n"
                          "Pode retirar o ticket."))
        

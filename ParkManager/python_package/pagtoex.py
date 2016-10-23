# -*- coding: utf-8 -*-
from .ui.pagamento import Ui_Pagto
from .communicate import Communicate
from .db import DB
from .printer import Printer, PrintTemplate
from configparser import ConfigParser
from PyQt5 import QtWidgets, QtCore, QtGui
from datetime import datetime


class PagtoEx(QtWidgets.QWidget, Ui_Pagto):
    searchquery = ("SELECT id, dia, hora, placa, marca, modelo, cor "
                   "FROM entrada WHERE id = %(id)s")
    searchqueryplaca = ("SELECT  id, dia, hora, placa, marca, modelo, cor "
                        "FROM entrada WHERE placa = %(placa)s "
                        "ORDER BY dia desc, hora desc")
    addquery = ("INSERT INTO pagto (ent_id, dia, hora, valor) "
                "VALUES (%(ent_id)s, %(dia)s, %(hora)s, %(valor)s)")
    searchpgto = ("SELECT id FROM pagto WHERE ent_id = %(id)s")
    
    def __init__(self, parent=None, csignal=None, cfgfile=None,
                 printer=None):
        super().__init__(parent)
        
        if csignal is None:
            self.csignal = Communicate()
        else:
            self.csignal = csignal

        self.printer = printer
            
        self.ui = Ui_Pagto()
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

        currency = QtGui.QDoubleValidator(parent=self.ui.recebidoLE)
        currency.setDecimals(2)
        self.ui.recebidoLE.setValidator(currency)

        self.ui.placaLE.setReadOnly(False)
        
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
        self.ui.horaSaidaLE.setText(text)
        
    def showDate(self):
        date = QtCore.QDate.currentDate()
        text = date.toString("dd/MM/yyyy")
        self.ui.dataSaidaLE.setText(text)

    @QtCore.pyqtSlot(bool)
    def on_fecharButton_clicked(self):
        self.csignal.signal.emit()

    def closeEvent(self, event):
        self.csignal.signal.emit()

    @QtCore.pyqtSlot()
    def on_recebidoLE_editingFinished(self):
        try:
            text = float(self.ui.recebidoLE.text())
        except ValueError as err:
            self.msgBox("Separação de decimais com ponto(.) e não vígula (,).")
            return
        self.ui.recebidoLE.setText("{:.2f}".format(text))
        
    @QtCore.pyqtSlot(bool)
    def on_modificarCkB_clicked(self, status):
        if status:
            self.ui.dataSaidaLE.setReadOnly(False)
            self.timerdate.stop()
            self.ui.horaSaidaLE.setReadOnly(False)
            self.timer.stop()
        else:
            self.ui.dataSaidaLE.setReadOnly(True)
            self.timerdate.start(1000)
            self.ui.horaSaidaLE.setReadOnly(True)
            self.timer.start(1000)

    @QtCore.pyqtSlot(bool)
    def on_entModCkB_clicked(self, status):
        if status:
            self.ui.dataEntradaLE.setReadOnly(False)
            self.ui.horaEntradaLE.setReadOnly(False)
            self.ui.marcaLE.setReadOnly(False)
            self.ui.modeloLE.setReadOnly(False)
            self.ui.corLE.setReadOnly(False)
        else:
            self.ui.dataEntradaLE.setReadOnly(True)
            self.ui.horaEntradaLE.setReadOnly(True)
            self.ui.marcaLE.setReadOnly(True)
            self.ui.modeloLE.setReadOnly(True)
            self.ui.corLE.setReadOnly(True)

    @QtCore.pyqtSlot(bool)
    def on_novoButton_clicked(self):
        self.ui.ticketEntradaLE.clear()
        self.ui.dataSaidaLE.clear()
        self.ui.horaSaidaLE.clear()
        self.ui.dataEntradaLE.clear()
        self.ui.horaEntradaLE.clear()
        self.ui.valorLE.clear()
        self.ui.recebidoLE.clear()
        self.ui.trocoLE.clear()
        self.ui.placaLE.clear()
        self.ui.marcaLE.clear()
        self.ui.modeloLE.clear()
        self.ui.corLE.clear()
        self.ui.modificarCkB.setCheckState(QtCore.Qt.Unchecked)
        self.showDate()
        self.showTime()
        self.timer.start(1000)

    @QtCore.pyqtSlot(bool)
    def on_procurarButton_clicked(self):
        config = ConfigParser()
        config.read_file(open(self.cfgfile))

        searchbyno = True
        ent_id = self.ui.ticketEntradaLE.text()
        values = {'id': ent_id}
        
        values['placa'] = self.ui.placaLE.text()
        if not values['placa'] and not ent_id:
            self.msgBox("Campo Ticket Entrada e Placa Vazios.")
            return

        if not ent_id:
            searchbyno = False
        
        # busca no bd
        db = DB()
        if searchbyno:
            result = db.fetchone(self.searchquery, values)
        else:
            result = db.fetchall(self.searchqueryplaca, values)[0]
        if not result:
            self.msgBox("Ticket não existente.")
            db.close()
            return

        payed = {}
        if searchbyno:
            payed['id'] = ent_id
        else:
            payed['id'] = result[0]

        result_pagto = db.fetchone(self.searchpgto, payed)
        if result_pagto:
            self.msgBox("Ticket já pago.")
            db.close()
            return
            
        db.close()

        # retorno:
        # dia = datetime.date, hora = datetime.timedelta
        # placa, marca, modelo e cor string
        
        # escrevendo nos campos
        keys = ('id', 'dataEntrada', 'horaEntrada', 'placa', 'marca',
                'modelo', 'cor')
        for k, v in zip(keys, result):
            values[k] = v

        values['dataEntrada'] = result[1].strftime("%d/%m/%Y")
        self.ui.dataEntradaLE.setText(values['dataEntrada'])

        values['horaEntrada'] = "{0:0>8}".format(str(result[2]))
        self.ui.horaEntradaLE.setText(values['horaEntrada'])

        if not searchbyno:
            self.ui.ticketEntradaLE.setText(str(values['id']))
        self.ui.placaLE.setText(values['placa'])
        self.ui.marcaLE.setText(values['marca'])
        self.ui.modeloLE.setText(values['modelo'])
        self.ui.corLE.setText(values['cor'])

        # gerando o valor da estadia 30m 1h 8h
        strsai = " ".join((self.ui.dataSaidaLE.text(),
                           self.ui.horaSaidaLE.text()))
        now = datetime.strptime(strsai, "%d/%m/%Y %H:%M:%S")

        strent = " ".join((values['dataEntrada'], str(result[2])))
        ent = datetime.strptime(strent, "%d/%m/%Y %H:%M:%S")

        dt = now - ent
        tsec = int(dt.total_seconds())

        dth = tsec // 3600
        dtm = (tsec // 60) % 60
        tempo_est = "{:0>2}:{:0>2}".format(dth, dtm)

        valor = 0
        self.ui.permanenciaLE.setText(tempo_est)
        if dth >= 8:
            valor = float(config['Valores']['diaria'])
        else:
            valor = dth * float(config['Valores']['hora'])
            if dtm <= 30:
                valor += float(config['Valores']['meia'])
            else:
                valor += float(config['Valores']['hora'])

        self.ui.valorLE.setText("{:.2f}".format(valor))

    @QtCore.pyqtSlot(bool)
    def on_calcularButton_clicked(self):
        try:
            valor = float(self.ui.valorLE.text())
            recebido = float(self.ui.recebidoLE.text())
        except ValueError as err:
            self.msgBox("Campos valor e recebido não podem ser vazios.")
            return

        troco = recebido - valor
        if troco < 0:
            self.msgBox(("Campo recebido precisa ser maior "
                         "do que o campo valor."))
        
        self.ui.trocoLE.setText("{:.2f}".format(troco))

    @QtCore.pyqtSlot(bool)
    def on_imprimirButton_clicked(self):
        # dia formato dia/mes/ano para ano-mes-dia
        dataSaida = QtCore.QDate.fromString(self.ui.dataSaidaLE.text(),
                                            "dd/MM/yyyy")
        
        values = {'ent_id': self.ui.ticketEntradaLE.text(),
                  'dia': dataSaida.toString("yyyy-MM-dd"),
                  'hora': self.ui.horaSaidaLE.text(),
                  'valor': self.ui.valorLE.text()}

        others = {'Recebido': self.ui.recebidoLE.text(),
                  'Troco': self.ui.trocoLE.text(),
                  'Data Entrada': self.ui.dataEntradaLE.text(),
                  'Hora Entrada': self.ui.horaEntradaLE.text(),
                  'Placa': self.ui.placaLE.text(),
                  'Marca': self.ui.marcaLE.text(),
                  'Modelo': self.ui.modeloLE.text(),
                  'Cor': self.ui.corLE.text(),
                  'Permanência': self.ui.permanenciaLE.text()}
        
        # validando as variaveis
        if len(values['dia']) < 10 or len(values['hora']) < 8 or \
           not values['valor'] or float(values['valor']) < 0 or \
           not values['ent_id']:
            self.msgBox((u"Preenchimento incorreto. "
                         u"Todos campos são obrigatórios."))
            return

        for k, v in others.items():
            if not v:
                self.msgBox((u"Preenchimento incorreto do campo {}. "
                             u"Todos campos são obrigatórios.").format(k))
                return

        # Inserindo no bd
        db = DB()
        search = {'id': values['ent_id']}
        result = db.fetchone(self.searchpgto, search)
        if result:
            self.msgBox("Ticket já pago.")
            db.close()
            return

        others['Ticket Saída'] = db.insert(self.addquery, values)
        db.close()

        # Imprimindo comprovante
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
        line = "Ticket Saida : {0:0>10}".format(others['Ticket Saída'])
        ptr.writelncenter(line)
        line = "Ticket Entrada : {0:0>10}".format(values['ent_id'])
        ptr.writelncenter(line)

        # marca, modelo e cor
        line = others['Marca'] + " " + others['Modelo'] + " " + others['Cor']
        if len(line) < 48:
            ptr.writelncenter(line)
        else:
            ptr.writeln("Marca  : "+others['Marca'])
            ptr.writeln("Modelo : "+others['Modelo'])
            ptr.writeln("Cor    : "+others['Cor'])
        # placa
        line = "Placa : " + others['Placa']
        ptr.writeln(line)
        
        # data e Hora de entrada
        ptr.writeln("")
        ptr.writeln("Data Entrada : "+others['Data Entrada'])
        ptr.writeln("Hora Entrada : "+others['Hora Entrada'])
        ptr.writeln("Data Saida   : "+dataSaida.toString("dd/MM/yyyy"))
        ptr.writeln("Hora Saida   : "+values['hora'])
        ptr.writeln("Permanencia  : "+others['Permanência'])

        # Valores
        ptr.writeln("")
        ptr.writeln("Valor Pago         :"+others['Recebido'])
        ptr.writeln("Valor Permanencia  :"+values['valor'])
        ptr.writeln("")
        ptr.writeln("Troco              :"+others['Troco'])

        ptr.writeln("")
        ptr.writeln(template.separator)
        
        ptr.close()
        self.timedMsgBox(("Impressão finalizada.\n"
                          "Pode retirar o ticket."))


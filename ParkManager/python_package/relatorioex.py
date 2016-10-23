# -*- coding: utf-8 -*-
from .ui.relatorio import Ui_Relatorio
from .communicate import Communicate
from .db import DB
from PyQt5 import QtWidgets, QtCore
import os
import csv


class RelatorioEx(QtWidgets.QWidget, Ui_Relatorio):
    searchquery = ("SELECT dia, valor FROM pagto "
                   "WHERE (dia BETWEEN %(dini)s AND %(dfin)s)")
    header = ["Data", "Qtd de Carros", "Valor Total"]

    def __init__(self, parent=None, csignal=None, cfgfile=None):
        super().__init__(parent)

        if csignal is None:
            self.csignal = Communicate()
        else:
            self.csignal = csignal

        self.ui = Ui_Relatorio()
        self.ui.setupUi(self)
        self.cfgfile = cfgfile

        self.ui.datainiDE.setDate(QtCore.QDate.currentDate())
        self.ui.datafinDE.setDate(QtCore.QDate.currentDate())
        
        self.ui.resTable.setRowCount(1)
        self.ui.resTable.setColumnCount(len(self.header))
        self.ui.resTable.setHorizontalHeaderLabels(self.header)
        
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
    def on_procurarButton_clicked(self):
        search = {'dini': self.ui.datainiDE.date().toString("yyyy-MM-dd"),
                  'dfin': self.ui.datafinDE.date().toString("yyyy-MM-dd")}

        db = DB()
        res = db.fetchall(self.searchquery, search)
        if not res or res is None:
            self.msgBox("A pesquisa não retornou nenhum resultado.")
            db.close()
            return
        db.close()
        
        values = {}
        for r in res:
            date = r[0].strftime("%d/%m/%Y")
            values[date] = {'qtd': 0,
                            'valor': 0}
        values['Total'] = {'qtd': 0,
                           'valor': 0}
        for r in res:
            date = r[0].strftime("%d/%m/%Y")
            values[date]['qtd'] += 1
            values[date]['valor'] += r[1]
            values['Total']['qtd'] += 1
            values['Total']['valor'] += r[1]

        keys = sorted(values.keys())
        row_keys = ['qtd', 'valor']
        self.ui.resTable.setRowCount(len(keys))
        for i, row in enumerate(keys):
            cel = QtWidgets.QTableWidgetItem(row)
            self.ui.resTable.setItem(i, 0, cel)
            for j, col in enumerate(row_keys, start=1):
                cel = QtWidgets.QTableWidgetItem(str(values[row][col]))
                cel.setTextAlignment(QtCore.Qt.AlignCenter)
                self.ui.resTable.setItem(i, j, cel)

    @QtCore.pyqtSlot(bool)
    def on_csvButton_clicked(self):
        root = os.path.abspath('.')
        csvdir = os.path.join(root, "csv")
        win = QtWidgets.QFileDialog()
        filename = win.getSaveFileName(self, "Salvar Arquivo",
                                       csvdir, ("Todos Arquivos CSV (*.csv);;"
                                                " Todos Arquivos (*.*)"))
        
        if not filename[0]:
            self.msgBox("Arquivo não criado.")
            return

        values = {'dini': self.ui.datainiDE.date().toString("yyyy-MM-dd"),
                  'dfin': self.ui.datafinDE.date().toString("yyyy-MM-dd")}
        
        with open(filename[0], "w") as fout:
            writer = csv.writer(fout, delimiter=';')
            # header
            writer.writerow(["Data inicial", values['dini']])
            writer.writerow(["Data final", values['dfin']])
            writer.writerow(["Data", "Qtd de Carros", "Valor Total"])

            # Contents
            for i in range(self.ui.resTable.rowCount()):
                row = []
                for j in range(self.ui.resTable.columnCount()):
                    row.append(self.ui.resTable.item(i, j).text())
                writer.writerow(row)

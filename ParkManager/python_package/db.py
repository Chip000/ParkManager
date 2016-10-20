# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
try:
    import mysql.connector as mariadb
except ImportError:
    import pymysql as mariadb
import keyring
import os


class DB(object):
    user = 'parkmanagerpy'
    pwd = keyring.get_password('parkmanager', 'parkmanagerpy')
    host = 'localhost'
    database = 'parkmanagerdb'
    
    def __init__(self):
        try:
            self.cnx = mariadb.connect(user=self.user,
                                       password=self.pwd,
                                       host=self.host,
                                       database=self.database)
        except mariadb.Error as err:
            if err.errno == mariadb.errorcode.ER_ACCESS_DENIED_ERROR:
                self.msgBox(u"BD: Usuário ou Senha errada.")
            elif err.errno == mariadb.errorcode.ER_BAD_DB_ERROR:
                self.msgBox(u"Banco de dados não existe.")
            else:
                self.msgBox(u"Erro.", inftext=err)
                
    def msgBox(self, text=None, inftext=None):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle(u"Erro")
        msg.setText(text)
        if inftext is not None:
            msg.setInformativeText(inftext)
        msg.exec_()
        
    def close(self):
        self.cnx.close()
        
    def insert(self, query=None, params=None):
        # Retorna o id da insercao
        self.cursor = self.cnx.cursor()
        try:
            self.cursor.execute(query, params)
            self.cnx.commit()
        except Exception as err:
            self.msgBox(u"Erro; {}".format(err))

        rowid = self.cursor.lastrowid
        self.cursor.close()
        return rowid

    def fetchone(self, query=None, params=None):
        # Retorna apenas um resultado
        self.cursor = self.cnx.cursor()
        try:
            self.cursor.execute(query, params)

            row = self.cursor.fetchone()
        except Exception as err:
            self.msgBox(u"Erro; {}".format(err))
            row = None

        self.cursor.close()
        return row
    
    def fetchall(self, query=None, params=None):
        # Retorna todos resultados em uma tupla
        self.cursor = self.cnx.cursor()
        try:
            self.cursor.execute(query, params)

            res = self.cursor.fetchall()
        except Exception as err:
            self.msgBox(u"Erro; {}".format(err))
            res = None

        self.cursor.close()
        return res
    
    def backup(self, path=None):
        if path is None:
            raise ValueError

        today = QtCore.QDate.currentDate()
        dayofweek = today.toString("ddd").lower()

        filename = "backup." + dayofweek
        fullpath = os.path.join(path, filename)
        
        bkpcmd = "mysqldump -u {} -p{} {} > {}"

        os.system(bkpcmd.format(self.user, self.pwd, self.database, fullpath))


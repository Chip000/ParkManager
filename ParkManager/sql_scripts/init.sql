CREATE USER IF NOT EXISTS 'parkmanagerpy'@'localhost'
	   IDENTIFIED BY '# Inserir password';
CREATE DATABASE IF NOT EXISTS parkmanagerdb;
GRANT ALL PRIVILEGES ON parkmanagerdb.* TO 'parkmanagerpy'@'localhost';
REVOKE CREATE ON parkmanagerdb.* FROM 'parkmanagerpy'@'localhost';
REVOKE DROP ON parkmanagerdb.* FROM 'parkmanagerpy'@'localhost';
REVOKE GRANT OPTION ON parkmanagerdb.* FROM 'parkmanagerpy'@'localhost';
FLUSH PRIVILEGES;

SELECT DISTINCT User FROM mysql.user;

USE parkmanagerdb;
CREATE TABLE IF NOT EXISTS entrada (
	   id int(10) NOT NULL AUTO_INCREMENT,
	   dia date NOT NULL,
	   hora time NOT NULL,
	   placa varchar(7) NOT NULL,
	   marca varchar(30) NOT NULL,
	   modelo varchar(30) NOT NULL,
	   cor varchar(20) NOT NULL,
	   PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS pagto (
	   id int(10) NOT NULL AUTO_INCREMENT PRIMARY KEY,
	   ent_id int(10) NOT NULL,
	   dia date NOT NULL,
	   hora time NOT NULL,
	   valor decimal(11, 2) NOT NULL,
	   CONSTRAINT `fk_entrada_pagto`
		FOREIGN KEY (ent_id) REFERENCES entrada (id)
		ON DELETE CASCADE
		ON UPDATE RESTRICT
);

SHOW tables;

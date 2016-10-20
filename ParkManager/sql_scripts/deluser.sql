SHOW tables IN parkmanagerdb;
DROP TABLE IF EXISTS parkmanagerdb.pagto;
DROP TABLE IF EXISTS parkmanagerdb.entrada;
SHOW tables IN parkmanagerdb;

DROP USER IF EXISTS 'parkmanagerpy'@'localhost';
SELECT DISTINCT User FROM mysql.user;

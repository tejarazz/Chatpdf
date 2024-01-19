# db.py

from flask_mysqldb import MySQL
from flask import Flask


def configure_database(app=None):
    if app is not None:
        app.config.from_object('config.Config')
        mysql = MySQL(app)
    else:
        mysql = MySQL()

    return mysql

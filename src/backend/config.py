import mysql.connector
from mysql.connector import Error


class Config:
    DEBUG = True

    # DB
    MYSQL_HOST = '127.0.0.1'
    MYSQL_USER = 'dev'
    MYSQL_PASSWORD = 'PDFQuery@dev'
    MYSQL_DB = 'PDFCHAT'

    # App
    UPLOAD_FOLDER = '/tmp/'

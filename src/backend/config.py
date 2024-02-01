import os


class Config:
    DEBUG = True

    # DB
    MYSQL_HOST = '127.0.0.1'
    MYSQL_USER = 'dev'
    MYSQL_PASSWORD = 'PDFQuery@dev'
    MYSQL_DB = 'PDFCHAT'

    # App
    UPLOAD_FOLDER = os.getenv('PDF_FILE_UPLOAD_DIR', 'D://uploads')

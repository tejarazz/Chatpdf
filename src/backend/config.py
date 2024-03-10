import os


class Config:
    DEBUG = True

    # DB
    MYSQL_HOST = os.environ['DB_HOST']
    MYSQL_USER = os.environ['DB_USER']
    MYSQL_PASSWORD = os.environ['DB_PASSWORD']
    MYSQL_DB = os.environ['DB_DATABASE']

    # App
    UPLOAD_FOLDER = os.getenv('PDF_FILE_UPLOAD_DIR', 'D://uploads')

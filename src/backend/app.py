# app.py

from routes import  ask_question, create_chat, delete_chat, file_upload, list_all_chats,get_user_details
from routes import load_chat, remove_document, list_files, update_chat_name,login,sign_up, logout
from flask import Flask
from flask_cors import CORS
from db import configure_database
from models import create_tables
from flask_session import Session



def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key_here'  # Set a secret key for session encryption
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR']='./sessions'

    Session(app)
    CORS(app)
    mysql = configure_database(app)

    # Create tables on startup
    create_tables()

    # Include other route files

    # File upload route
    app.add_url_rule('/file-upload', 'file_upload',
                     file_upload, methods=['POST'])

    # Chat operations routes
    app.add_url_rule('/list-all-chats', 'list_all_chats',
                     list_all_chats, methods=['GET'])
    app.add_url_rule('/create-chat', 'create_chat',
                     create_chat, methods=['POST'])
    app.add_url_rule('/remove-document/<int:chat_id>',
                     'remove_document', remove_document, methods=['DELETE'])
    app.add_url_rule('/delete-chat/<int:chat_id>',
                     'delete_chat', delete_chat, methods=['DELETE'])
    app.add_url_rule('/load-chat/<int:chat_id>',
                     'load_chat', load_chat, methods=['GET'])
    app.add_url_rule('/ask-question/<int:chat_id>',
                     'ask_question', ask_question, methods=['POST'])
    app.add_url_rule('/update_chatname',
                     'update_chatname', update_chat_name, methods=['POST'])
    app.add_url_rule('/login',
                     'login', login, methods=['POST'])
    app.add_url_rule('/sign_up',
                     'sign_up', sign_up, methods=['POST'])
    app.add_url_rule('/logout',
                    'logout', logout, methods=['GET'])
    app.add_url_rule('/get_user_details', 'get_user_details', get_user_details, methods=['GET'])
    # New route to list all files
    app.add_url_rule('/list-files', 'list_files', list_files, methods=['GET'])

    return app


if __name__ == '__main__':
    create_app().run()

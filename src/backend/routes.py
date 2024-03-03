import os
from flask import Flask, request, jsonify
from modules.fileprocess import fileprocess, save_conversation, store_chat_info, load_chat_data,rem_doc
from modules.fileprocess import load_chat_list, del_chat, update_chatname, get_embeddings_of_doc
from modules.fileprocess import get_similar_chunks,  load_file_list,loginform,signup_form,get_user_info
from config import Config
from werkzeug.utils import secure_filename
from datetime import datetime
import tiktoken
from utilities import getResponseFromMessages, get_token_count, select_messages_within_token_limit
import json
from flask import request, session, make_response
import uuid


def login():
    username = request.form.get('username')
    password = request.form.get('password')
    login_status, user_id = loginform(username, password)
    if login_status:
        response = make_response(jsonify({"message": "login successful", "username": username}))
        session['sid'] = str(uuid.uuid4())
        session['userid'] = user_id
        # Set the cookie
        response.set_cookie('sid', str(session['sid']))
        return response, 200
    else:
        response = make_response(jsonify({"message": "login failed"}))
        return response, 401
    
    
    
def logout():
    # Create a response
    response = make_response(jsonify({"message": "Logged out successfully"}))
    
    # Delete all cookies
    cookies_to_delete = request.cookies.keys()
    for cookie_name in cookies_to_delete:
        response.delete_cookie(cookie_name)
    
    return response, 200

def sign_up():
    username = request.form.get('username')
    email = request.form.get('email')
    password_hash = request.form.get('password')

    user_creation_status, message = signup_form(username, email, password_hash)
    if user_creation_status:
        return jsonify({"message": "User created"}), 200
    else:
        return jsonify({"message": message}), 409
    
    
    
def get_user_details():
    b_sid  = request.cookies.get('sid', None)
    s_sid = session.get('sid', None)
    user_id = session['userid']
    if not (b_sid and b_sid == s_sid):
        return jsonify({"error": 'Authorization Error'}), 401
    username = get_user_info(user_id)   
    if username:
        return jsonify({"message": "User details found","username":username ,"user_id":user_id}), 200   
    else:
        return jsonify({"message": "User details not found"}), 404
    
def file_upload():
    try:
        b_sid  = request.cookies.get('sid', None)
        s_sid = session.get('sid', None)
        user_id = session['userid']
        if not (b_sid and b_sid == s_sid):
            return jsonify({"error": 'Authorization Error'}), 401
        UPLOAD_FOLDER = Config.UPLOAD_FOLDER
        # Check if the POST request has a file part
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']

        # Check if the user does not select a file
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Ensure the specified directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Save the file to the specified directory on the "D" drive
        file_path = os.path.join(
            UPLOAD_FOLDER, f"{secure_filename(file.filename)}")
        file.save(file_path)

        fileprocess(file_path, user_id)
        if os.path.exists(file_path) and file_path.endswith('.pdf'):
            os.remove(file_path)

        return jsonify({"message": "File uploaded successfully", "file_name": file.filename}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def list_files():
    try:
        b_sid  = request.cookies.get('sid', None)
        s_sid = session.get('sid', None)
        user_id = session['userid']
        if not (b_sid and b_sid == s_sid):
            return jsonify({"error": 'Authorization Error'}), 401
        UPLOAD_FOLDER = Config.UPLOAD_FOLDER
        status, content = load_file_list(user_id)
        if status:
            return jsonify({"files": content}), 200
        else:
            return jsonify({"files": []}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


def list_all_chats():
    try:
        # Get the chat_id parameter from the query string
        # chat_id = request.args.get('chat_id')
        b_sid  = request.cookies.get('sid', None)
        s_sid = session.get('sid', None)
        user_id = session['userid']
        if not (b_sid and b_sid == s_sid):
            return jsonify({"error": 'Authorization Error'}), 401
        success, chat_data = load_chat_list(user_id)

        # Check if chat_data retrieval was successful
        if success:
            # Return the chat data as JSON
            return jsonify(chat_data)
        else:
            # If chat_id not found or other errors, return an error response
            return jsonify({"error": chat_data["error"]}), 404 if "Chat not found" in chat_data["error"] else 500

    except Exception as e:
        # Handle other potential errors
        return jsonify({"error": str(e)}), 500


def create_chat():
    try:
        data = request.get_json()
        file_names = data['fileNames']

        b_sid  = request.cookies.get('sid', None)
        s_sid = session.get('sid', None)
        user_id = session['userid']
        if not (b_sid and b_sid == s_sid):
            return jsonify({"error": 'Authorization Error'}), 401

        # Store chat information and retrieve the chat_id
        stored_chat_id = store_chat_info(file_names, user_id)

        # # Convert the stored_chat_id to an integer
        # stored_chat_id = int(
        #     stored_chat_id) if stored_chat_id is not None else None

        # Return chat_id as a numeric value in the response along with a success message
        return jsonify({'message': f'Chat created successfully with files: {", ".join(file_names)}', 'chat_id': stored_chat_id}), 200
    except Exception as e:
        return jsonify({'error': f'{str(e)}. Files: {", ".join(file_names)}', 'chat_id': None}), 400



def remove_document(chat_id):
    try:
        pass
    except Exception as e:
    # Handle other potential errors and return an error message
        print("An exception occurred:", e)
        return jsonify({"error": str(e)}), 500

def delete_chat(chat_id):
    try:
        
        b_sid  = request.cookies.get('sid', None)
        s_sid = session.get('sid', None)
        user_id = session['userid']
        if not (b_sid and b_sid == s_sid):
            return jsonify({"error": 'Authorization Error'}), 401
        # Call the del_chat function to delete the chat
        success, result = del_chat(chat_id,user_id)

        if success:
            return jsonify(result)
        else:
            return jsonify(result), 404

    except Exception as e:
        # Handle other potential errors and return an error message
        print("An exception occurred:", e)
        return jsonify({"error": str(e)}), 500


def load_chat(chat_id):
    try:
        # Get the chat_id parameter from the query string
        # chat_id = request.args.get('chat_id')
        
        
        b_sid  = request.cookies.get('sid', None)
        s_sid = session.get('sid', None)
        user_id = session['userid']
        if not (b_sid and b_sid == s_sid):
            return jsonify({"error": 'Authorization Error'}), 401
        success, chat_data = load_chat_data(chat_id,user_id)

        # Check if chat_data retrieval was successful
        if success:
            # Return the chat data as JSON
            return jsonify(chat_data)
        else:
            # If chat_id not found or other errors, return an error response
            return jsonify({"error": chat_data["error"]}), 404 if "Chat not found" in chat_data["error"] else 500

    except Exception as e:
        # Handle other potential errors
        return jsonify({"error": str(e)}), 500


def update_chat_name():
    try:
        # Get parameters from the request (assuming JSON data is sent in the request body)
        data = request.get_json()
        chat_id = data.get('chat_id')
        new_chat_name = data.get('new_chat_name')
        b_sid  = request.cookies.get('sid', None)
        s_sid = session.get('sid', None)
        user_id = session['userid']
        if not (b_sid and b_sid == s_sid):
            return jsonify({"error": 'Authorization Error'}), 401

        # Call the function to update the chat name
        success, result = update_chatname(chat_id, new_chat_name,user_id)

        if success:
            return jsonify(result)
        else:
            return jsonify({"error": result["error"]}), 500

    except Exception as e:
        # Handle other potential errors
        return jsonify({"error": str(e)}), 500


def ask_question(chat_id):
    try:
        
        b_sid  = request.cookies.get('sid', None)
        s_sid = session.get('sid', None)
        user_id = session['userid']
        if not (b_sid and b_sid == s_sid):
            return jsonify({"error": 'Authorization Error'}), 401
        
        question_text = request.form.get('question')
        if not question_text:
            return jsonify({"error": "Question parameter is missing"}), 400
        
        
        status, data = load_chat_data(chat_id,user_id)
        # Extract document name from the chat(data)

        doc_names = data["documents"]

        # Fetch the embeddings from the document name

        embs = [get_embeddings_of_doc(doc_name)[1] for doc_name in doc_names]

        # print(get_embeddings_of_doc(doc_names[0])[1]['embeddings_json']["0"])
        # Find the similarities of each embedding chunk with the question.Also find the top similar chunks.

        page_data_docs = [get_similar_chunks(
            data_, question_text) for data_ in embs]
        top_page_data_list = [
            page_data for page_data_list in page_data_docs for page_data in page_data_list]

        top_page_data_list_sorted = sorted(
            top_page_data_list, key=lambda x: x['score'])[::-1]
        combined_text = ''
        token_counter_page_data = 0
        max_page_data_tokens = 1600
        for page_data in top_page_data_list_sorted:
            token_counter_page_data += get_token_count(page_data['text'])
            if token_counter_page_data <= max_page_data_tokens:
                combined_text += page_data['text']

        # Design a prompt that takes the top similar chunks and asks the question to LLM.

        question_prompt = f'''
You are a question answering specialist. Using the SOURCE TEXT provided in triple backticks, answer the QUESTION provided in triple backticks.

SOURCE TEXT: ```{combined_text}```

QUESTION: ```{question_text}```

ANSWER:
'''

        messages = data['conversation']
        messages_q = data['conversation'].copy()

        selected_messages, current_token_count = select_messages_within_token_limit(
            messages_q)
        q = {
            "role": "user",
            "content": question_text
        }
        q_prompt = {
            "role": "user",
            "content": question_prompt
        }
        messages.append(q)
        selected_messages.append(q_prompt)
        response = getResponseFromMessages(selected_messages)

        a = {
            "content": response,
            "role": "assistant"
        }
        messages.append(a)
        part_conv = []
        part_conv.append(q)
        part_conv.append(a)
        chat_name = data["chat_name"]
        if len(messages) <= 2:
            messages_dum = []

            # Multi-Shot Prompting
            q = {
                "role": "user",
                "content": f'''Summarize the text provided in triple backticks in maximum 3 words. This will be used to recall this text using the summary generated. Take a hint from examples.
                
                EXAMPLE 1:
                TEXT: Who is president of USA? I'm sorry, but I don't have real-time information. As of my last knowledge update in January 2022, Joe Biden was the President of the United States. Please verify with up-to-date sources to find the current President as my information might be outdated.
                SUMMARY: Biden is US President.
                
                EXAMPLE 2:
                TEXT: Suggest good books to read in myth? Certainly! Mythology is a rich and fascinating genre with a wide range of cultural and historical stories. Here are some excellent books in the realm of mythology:
"The Hero with a Thousand Faces" by Joseph Campbell
A classic exploration of the hero's journey and common mythological themes across cultures.
"Norse Mythology" by Neil Gaiman
Gaiman retells the classic Norse myths in his unique and engaging style.
"Bulfinch's Mythology" by Thomas Bulfinch
A compilation of Greek, Roman, and Norse mythology, providing a comprehensive overview.
                SUMMARY:Mythology Book Recommendations
                
                Text:`{question_text}? {response}`
                SUMMARY: '''
            }

            messages_dum.append(q)
            chat_name = getResponseFromMessages(messages_dum)
        save_conversation(messages, chat_id, user_id, chat_name)
        return jsonify({"conversation": part_conv, "chat_name": chat_name})

    except Exception as e:
        print(f"Error in ask_question route: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

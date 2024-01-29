import os
from flask import Flask, request, jsonify
from modules.fileprocess import fileprocess, save_conversation, store_chat_info, load_chat_data, load_chat_list, del_chat, update_chatname, get_embeddings_of_doc, get_similar_chunks
from config import Config
from werkzeug.utils import secure_filename
from datetime import datetime
from utilities import getResponseFromMessages
import json


def file_upload():
    try:
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

        print(fileprocess(file_path, 1))

        return jsonify({"message": "File uploaded successfully", "file_name": file.filename}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def list_files():
    try:
        UPLOAD_FOLDER = Config.UPLOAD_FOLDER
        files = os.listdir(UPLOAD_FOLDER)
        file_list = []

        for file in files:
            file_path = os.path.join(UPLOAD_FOLDER, file)
            file_info = {
                'file_name': file,
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'last_modified': os.path.getmtime(file_path)
            }
            file_list.append(file_info)

        return jsonify({"files": file_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def list_all_chats():
    # Implement logic to list all chats

    try:
        # Get the chat_id parameter from the query string
        # chat_id = request.args.get('chat_id')

        success, chat_data = load_chat_list()

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

        # Assuming user_id is available, replace with the actual user_id
        user_id = 1  # Replace with the actual user_id

        # Store chat information and retrieve the chat_id
        stored_chat_id = store_chat_info(file_names, user_id)

        print(stored_chat_id)

        # # Convert the stored_chat_id to an integer
        # stored_chat_id = int(
        #     stored_chat_id) if stored_chat_id is not None else None

        # Return chat_id as a numeric value in the response along with a success message
        return jsonify({'message': f'Chat created successfully with files: {", ".join(file_names)}', 'chat_id': stored_chat_id}), 200
    except Exception as e:
        return jsonify({'error': f'{str(e)}. Files: {", ".join(file_names)}', 'chat_id': None}), 400


def add_document(chat_id):

    return jsonify({"message": "Document added succesfully"})


def remove_document(chat_id):
    # Implement logic to remove a document from a chat
    return jsonify({"message": "Document removed from chat"})


def delete_chat(chat_id):
    try:
        # Call the del_chat function to delete the chat
        success, result = del_chat(chat_id)

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

        success, chat_data = load_chat_data(chat_id)

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

        # Call the function to update the chat name
        success, result = update_chatname(chat_id, new_chat_name)

        if success:
            return jsonify(result)
        else:
            return jsonify({"error": result["error"]}), 500

    except Exception as e:
        # Handle other potential errors
        return jsonify({"error": str(e)}), 500


def ask_question(chat_id):
    try:
        question_text = request.form.get('question')
        if not question_text:
            return jsonify({"error": "Question parameter is missing"}), 400

        user_id = 1
        status, data = load_chat_data(chat_id)
        # Extract document name from the chat(data)

        doc_names = data["documents"]

        # Fetch the embeddings from the document name

        embs = [get_embeddings_of_doc(doc_name)[1] for doc_name in doc_names]

        print(get_embeddings_of_doc(doc_names[0])[1]['embeddings_json']["0"])
        # Find the similarities of each embedding chunk with the question.Also find the top similar chunks.

        similarity = [get_similar_chunks(
            data_, question_text) for data_ in embs]
        print(similarity)

        # TODO: design a prompt that takes the top similar chunks and asks the question to LLM.
        messages = data['conversation']
        q = {
            "role": "user",
            "content": question_text
        }
        messages.append(q)
        response = getResponseFromMessages(messages)

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
        save_conversation(messages, chat_id, chat_name)
        return jsonify({"conversation": part_conv})

    except Exception as e:
        print(f"Error in ask_question route: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

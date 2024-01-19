from utilities import read_pdf, runInsertQuery, get_text_embeddings, runSelectQuery, runSelectQuery
import os
import json


def fileprocess(file_path, user_id):
    print("file process started")

    try:
        output = read_pdf(file_path)
        op_string = json.dumps(output)
        emb_string = json.dumps(get_text_embeddings(output))
        filename = os.path.basename(file_path)

        ######

        insert_file_entry_query = '''
            INSERT INTO file_data (file_name, text_json, embeddings_json, user_id)
            VALUES (%s, %s, %s, %s)
        '''

        runInsertQuery(insert_file_entry_query,
                       (filename, op_string, emb_string, user_id))
        print("file process end")
        return True

    except Exception as e:
        print(f"Error in file processing: {str(e)}")
        return False


def save_conversation(conversation, chat_id, chat_name=None):
    try:
        chat_query = ', chat_name = %s' if chat_name else ""
        update_chat_query = f'''UPDATE pdfchat.chat_info
SET conversation = %s{chat_query} where chat_id =%s
        '''

        # Pass parameters as a tuple
        runInsertQuery(update_chat_query,
                       (json.dumps(conversation), chat_name, chat_id))
        return True

    except Exception as e:
        print("some error occured in save conversation", e)
        return False


def store_chat_info(documents, user_id):
    try:
        select_query = '''select max(chat_id) from chat_info'''
        result = runSelectQuery(select_query)
        last_chat_id = result[0][0]
        if last_chat_id:
            chat_id = last_chat_id+1
        else:
            chat_id = 0
        # Insert chat information without fetching results
        insert_query = '''
            INSERT INTO Chat_info (chat_id, chat_name, user_id, documents, conversation)
            VALUES (%s,%s, %s, %s, %s)
        '''
        values = (chat_id, '', user_id, json.dumps(documents), None)

        runInsertQuery(insert_query, values)
        return chat_id

    except Exception as e:
        print(f'Error in store_chat_info: {e}')
        return False


def load_chat_data(chat_id):
    try:
        # Query the database to retrieve chat data based on chat_id
        select_query = f'SELECT * FROM chat_info WHERE chat_id = {chat_id}'
        # values = (chat_id,)
        chat_data = runSelectQuery(select_query)
        print(chat_data)
        # Check if the chat_id exists in the database
        if chat_data:
            # Convert the messages column from string to list
            res = {
                'documents': [],
                'conversation': []
            }
            res['chat_id'] = chat_data[0][0]
            res['chat_name'] = chat_data[0][1]
            res['user_id'] = chat_data[0][2]
            if chat_data[0][3] is not None:
                res['documents'] = json.loads(chat_data[0][3])
            if chat_data[0][4] is not None:
                res['conversation'] = json.loads(chat_data[0][4])
            print(res)
            return True, res
        else:
            # If chat_id not found, return False and an error message
            return False, {"error": "Chat not found"}

    except Exception as e:
        # Handle other potential errors and return False and an error message
        print("some exception occured", e)
        return False, {"error": str(e)}


def load_chat_list():
    try:
        # Query the database to retrieve chat data based on chat_id
        select_query = f'SELECT chat_id, chat_name FROM chat_info'
        # values = (chat_id,)
        chat_data = runSelectQuery(select_query)
        print(chat_data)
        # Check if the chat_id exists in the database
        if chat_data:
            # Convert the messages column from string to list
            res = []
            for rec_tup in chat_data:
                rec = {

                }
                rec['chat_id'] = rec_tup[0]
                rec['chat_name'] = rec_tup[1]
                res.append(rec_tup)
            return True, res
        else:
            # If chat_id not found, return False and an error message
            return False, {"error": "Chat not found"}

    except Exception as e:
        # Handle other potential errors and return False and an error message
        print("some exception occured", e)
        return False, {"error": str(e)}

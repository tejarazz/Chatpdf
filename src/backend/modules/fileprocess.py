from utilities import read_pdf, runInsertQuery, get_text_embeddings, runSelectQuery, runSelectQuery, runDeleteQuery, runUpdateQuery, cosine_similarity, get_embeddings_of_text
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
        # Format the chat_query string using a ternary operator
        chat_query = ", chat_name = %s" if chat_name else ""

        # Correctly format the update_chat_query string
        update_chat_query = f'''UPDATE pdfchat.chat_info
SET conversation = %s{chat_query} WHERE chat_id = %s
        '''

        # Pass parameters as a tuple
        if chat_name:
            runInsertQuery(update_chat_query, (json.dumps(
                conversation), chat_name, chat_id))
        else:
            runInsertQuery(update_chat_query,
                           (json.dumps(conversation), chat_id))

        return True

    except Exception as e:
        print("Some error occurred in save conversation:", e)
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
                res.append(rec)
            return True, res
        else:
            # If chat_id not found, return False and an error message
            return False, {"error": "Chat not found"}

    except Exception as e:
        # Handle other potential errors and return False and an error message
        print("some exception occured", e)
        return False, {"error": str(e)}


def del_chat(chat_id):
    try:
        values = (chat_id,)
        # Delete the chat with the specified chat_id
        delete_query = 'DELETE FROM chat_info WHERE chat_id = %s'
        runDeleteQuery(delete_query, values)
        return True, {"message": "Chat deleted successfully"}

    except Exception as e:
        # Handle other potential errors and return False and an error message
        print("An exception occurred:", e)
        return False, {"error": str(e)}


def rem_doc(chat_id):
    try:
        values = (chat_id,)
        # Delete the chat with the specified chat_id
        delete_query = 'DELETE FROM chat_info WHERE documents = %s'
        runDeleteQuery(delete_query, values)
        return True, {"message": "Document removed successfully"}

    except Exception as e:
        # Handle other potential errors and return False and an error message
        print("An exception occurred:", e)
        return False, {"error": str(e)}


def update_chatname(chat_id, new_chat_name):
    try:
        values = (new_chat_name, chat_id)
        # update the chat with the specified chat_id
        update_query = 'UPDATE chat_info SET chat_name = %s WHERE chat_id = %s'
        runUpdateQuery(update_query, values)
        return True, {"message": "Chat name updated successfully"}

    except Exception as e:
        # Handle other potential errors and return False and an error message
        print("An exception occurred:", e)
        return False, {"error": str(e)}


def get_embeddings_of_doc(doc_name):

    try:
        fetch_filedata_query = f"SELECT text_json , embeddings_json FROM file_data WHERE file_name ='{doc_name}'"
        file_data = runSelectQuery(fetch_filedata_query)

        data = {

        }

        data['text_json'] = json.loads(file_data[0][0])
        data['embeddings_json'] = json.loads(file_data[0][1])

        return True, data

    except Exception as e:
        # Handle other potential errors and return False and an error message
        print("An exception occurred:", e)
        return False, {"error": str(e)}


# Find similar chunks from document

def get_similar_chunks(data, question):

    try:
        question_emb = get_embeddings_of_text(question)
        # print("Keys in embeddings_json:", data['embeddings_json'].keys())
        emb_similarity_scores = {page_no: cosine_similarity(
            question_emb, data['embeddings_json'][page_no]) for page_no in data['embeddings_json'].keys()}
        # Filter pages with similarity scores above or equal to the threshold
        relevant_page_nos = [page_no for page_no,
                             score in emb_similarity_scores.items() if score >= 0.4]
        print(emb_similarity_scores)
        print(relevant_page_nos)
        relevant_page_texts = {page_no: text for page_no,
                               text in data['text_json'].items() if page_no in relevant_page_nos}
        return relevant_page_texts

    except Exception as e:
        # Handle other potential errors and return False and an error message
        print("An exception occurred:", e)
        return False, {"error": str(e)}

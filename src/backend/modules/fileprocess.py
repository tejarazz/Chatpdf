from utilities import read_pdf, runInsertQuery, get_text_embeddings, runSelectQuery, runSelectQuery_with_values, runDeleteQuery, runUpdateQuery, cosine_similarity, get_embeddings_of_text
import os
import json


class UserIdTakenException(Exception):
    pass


class EmailTakenException(Exception):
    pass


def loginform(username, password):

    fetch_user_data_query = f"SELECT count(*), id FROM PDFCHAT.users where username =%s and password_hash=%s"

    res = runSelectQuery_with_values(
        fetch_user_data_query, (username, password))
    if res[0][0]:
        return True, res[0][1]
    else:
        return False, None


def signup_form(username, email, password_hash):
    try:

        print('pwd', password_hash)
        check_pre_signup_username_query = '''SELECT COUNT(*) FROM PDFCHAT.users WHERE username = %s'''
        check_pre_signup_email_query = '''SELECT COUNT(*) FROM PDFCHAT.users WHERE email = %s'''

        if runSelectQuery_with_values(check_pre_signup_username_query, (username,))[0][0]:
            raise UserIdTakenException
        if runSelectQuery_with_values(check_pre_signup_email_query, (email,))[0][0]:
            raise EmailTakenException

        insert_user_entry_query = '''
                    INSERT INTO PDFCHAT.users (username, email, password_hash) VALUES (%s, %s, %s)
                '''

        runInsertQuery(insert_user_entry_query,
                       (username, email, password_hash))
        return True, None
    except UserIdTakenException:
        return False, f'User Name - {username} is  already taken'
    except EmailTakenException:
        return False, f'Email - {email} is already in use'


def get_user_info(user_id):
    try:
        select_query = f'SELECT username FROM PDFCHAT.users WHERE id ={user_id}'
        # values = (chat_id,)
        user_data = runSelectQuery(select_query)
        if user_data:
            return user_data[0][0]
        else:
            raise Exception
    except Exception as e:
        print("some error occured", e)
        return None
    return False


def fileprocess(file_path, user_id):
    print("file process started")

    try:
        output = read_pdf(file_path)
        op_string = json.dumps(output)
        emb_string = json.dumps(get_text_embeddings(output))
        filename = os.path.basename(file_path)

        # Query the database to retrieve chat data based on chat_id
        count_files_with_filename_query = f"SELECT count(*) FROM PDFCHAT.file_data WHERE file_name = '{filename}' and user_id = {user_id}"

        # Update the embeddings and text in existing record
        if runSelectQuery(count_files_with_filename_query)[0][0]:
            update_query = f"""UPDATE PDFCHAT.file_data SET text_json = %s, embeddings_json = %s  WHERE file_name = '{filename}' and user_id = {user_id}"""
            runUpdateQuery(update_query, (op_string, emb_string))
            print('File Updated Successfully')
        else:
            # If record is not present already
            insert_file_entry_query = '''
                INSERT INTO PDFCHAT.file_data (file_name, text_json, embeddings_json, user_id)
                VALUES (%s, %s, %s, %s)
            '''

            runInsertQuery(insert_file_entry_query,
                           (filename, op_string, emb_string, user_id))
            print('File Inserted Successfully')
        return True

    except Exception as e:
        print(f"Error in file processing: {str(e)}")
        return False


def save_conversation(conversation, chat_id, user_id, chat_name=None):
    try:
        # Format the chat_query string using a ternary operator
        chat_query = ", chat_name = %s" if chat_name else ""

        # Correctly format the update_chat_query string
        update_chat_query = f'''UPDATE PDFCHAT.Chat_info
SET conversation = %s{chat_query} WHERE chat_id = %s and user_id = %s
        '''

        # Pass parameters as a tuple
        if chat_name:
            runInsertQuery(update_chat_query, (json.dumps(
                conversation), chat_name, chat_id, user_id))
        else:
            runInsertQuery(update_chat_query,
                           (json.dumps(conversation), chat_id, user_id))

        return True

    except Exception as e:
        print("Some error occurred in save conversation:", e)
        return False


def store_chat_info(documents, user_id):
    try:
        select_query = f'select max(chat_id) from PDFCHAT.Chat_info'
        result = runSelectQuery(select_query)
        last_chat_id = result[0][0]
        if last_chat_id:
            chat_id = last_chat_id+1
        else:
            chat_id = 0
        # Insert chat information without fetching results
        insert_query = '''
            INSERT INTO PDFCHAT.Chat_info (chat_id, chat_name, user_id, documents, conversation)
            VALUES (%s,%s, %s, %s, %s)
        '''
        values = (chat_id, '', user_id, json.dumps(documents), None)

        runInsertQuery(insert_query, values)
        return chat_id

    except Exception as e:
        print(f'Error in store_chat_info: {e}')
        return 1


def load_chat_data(chat_id, user_id):
    try:
        # Query the database to retrieve chat data based on chat_id
        select_query = f'SELECT * FROM PDFCHAT.Chat_info WHERE chat_id = {chat_id} and user_id ={user_id}'
        # values = (chat_id,)
        chat_data = runSelectQuery(select_query)
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
            return True, res
        else:
            # If chat_id not found, return False and an error message
            return False, {"error": "Chat not found"}

    except Exception as e:
        # Handle other potential errors and return False and an error message
        print("some exception occured", e)
        return False, {"error": str(e)}


def load_file_list(user_id):
    try:
        # Query the database to retrieve chat data based on chat_id
        select_query = f'SELECT file_name FROM PDFCHAT.file_data where user_id = {user_id}'
        # values = (chat_id,)
        file_data = runSelectQuery(select_query)
        # Check if the chat_id exists in the database
        if file_data:
            # Convert the messages column from string to list
            res = []
            for rec_tup in file_data:
                rec = {

                }
                rec['file_name'] = rec_tup[0]
                res.append(rec)
            return True, res
        else:
            return False, {"error": "Chat not found"}

    except Exception as e:
        # Handle other potential errors and return False and an error message
        print("some exception occured", e)
        return False, {"error": str(e)}


def load_chat_list(user_id):
    res = []
    try:
        # Query the database to retrieve chat data based on chat_id
        select_query = f'SELECT chat_id, chat_name FROM PDFCHAT.Chat_info where user_id = %s'
        # values = (chat_id,)
        chat_data = runSelectQuery_with_values(select_query, (user_id,))
        # Check if the chat_id exists in the database
        if chat_data:
            # Convert the messages column from string to list

            for rec_tup in chat_data:
                rec = {

                }
                rec['chat_id'] = rec_tup[0]
                rec['chat_name'] = rec_tup[1]
                res.append(rec)
        return True, res

    except Exception as e:
        # Handle other potential errors and return False and an error message
        print("some exception occured", e)
        return False, {"error": str(e)}


def del_chat(chat_id, user_id):
    try:
        values = (chat_id, user_id)
        # Delete the chat with the specified chat_id
        delete_query = 'DELETE FROM PDFCHAT.Chat_info WHERE chat_id = %s and user_id = %s'
        runDeleteQuery(delete_query, values)
        return True, {"message": "Chat deleted successfully"}

    except Exception as e:
        # Handle other potential errors and return False and an error message
        print("An exception occurred:", e)
        return False, {"error": str(e)}


def rem_doc(chat_id, user_id):
    try:
        values = (chat_id, user_id)
        # Adjusted the query to include 'chat_id=%s' in the deletion criteria
        delete_query = 'DELETE FROM PDFCHAT.Chat_info WHERE documents = %s AND user_id = %s AND chat_id = %s'
        runDeleteQuery(delete_query, values)
        return True, {"message": "Document removed successfully"}

    except Exception as e:
        # Catch specific exceptions if possible, and provide meaningful error messages
        print("An exception occurred:", e)
        return False, {"error": "Failed to remove document"}


def update_chatname(chat_id, new_chat_name, user_id):
    try:
        values = (new_chat_name, chat_id, user_id)
        # update the chat with the specified chat_id
        update_query = 'UPDATE PDFCHAT.Chat_info SET chat_name = %s WHERE chat_id = %s and user_id = %s'
        runUpdateQuery(update_query, values)
        return True, {"message": "Chat name updated successfully"}

    except Exception as e:
        # Handle other potential errors and return False and an error message
        print("An exception occurred:", e)
        return False, {"error": str(e)}


def get_embeddings_of_doc(doc_name):

    try:
        fetch_filedata_query = f"SELECT text_json , embeddings_json FROM PDFCHAT.file_data WHERE file_name ='{doc_name}'"
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

        total_pages = len(data['embeddings_json'])
        threshold = 0.4
        threshold_reducing_factor = 0.9

        emb_similarity_scores = {page_no: cosine_similarity(
            question_emb, data['embeddings_json'][page_no]) for page_no in data['embeddings_json'].keys()}

        def getRelevantPageNos(x): return [
            page_no for page_no, score in x.items() if score >= threshold]

        relevant_page_nos = getRelevantPageNos(emb_similarity_scores)

        if len(emb_similarity_scores.keys()) < 5:
            relevant_page_nos = list(emb_similarity_scores.keys())

        while (len(relevant_page_nos) < 5) and (len(emb_similarity_scores.keys()) >= 5):
            threshold *= threshold_reducing_factor
            # Filter pages with similarity scores above or equal to the threshold
            relevant_page_nos = getRelevantPageNos(emb_similarity_scores)

        page_data = [{'page_no': page_no, 'text': text, 'score': emb_similarity_scores[page_no]}
                     for page_no, text in data['text_json'].items() if page_no in relevant_page_nos]
        print(page_data)

        return page_data

    except Exception as e:
        # Handle other potential errors and return False and an error message
        print("An exception occurred:", e)
        return False, {"error": str(e)}

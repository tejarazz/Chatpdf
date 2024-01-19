# models.py
from utilities import runsqlQuery
import json


def create_users_table():
    query = '''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE,
        email VARCHAR(255) UNIQUE,
        password_hash VARCHAR(255)
    )
    '''
    runsqlQuery(query)

    # Insert initial data if not already present
    insert_query = '''
    INSERT IGNORE INTO users (username, email, password_hash)
    VALUES
        ('krishna teja', 'pb.saikrishnateja@gmail.com', '12345678')
    '''
    runsqlQuery(insert_query)


def create_file_data_table():
    query = '''
    CREATE TABLE IF NOT EXISTS file_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        file_name VARCHAR(255),
        text_json JSON,
        embeddings_json JSON,
        user_id INT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    '''
    runsqlQuery(query)


def create_questions_list_table():
    query = '''
    CREATE TABLE IF NOT EXISTS questions_list (
        id INT AUTO_INCREMENT PRIMARY KEY,
        question_text VARCHAR(255),
        embeddings_json JSON,
        user_id INT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    '''
    runsqlQuery(query)


def create_chat_info_table():
    query = '''
    CREATE TABLE IF NOT EXISTS Chat_info (
        chat_id INT AUTO_INCREMENT PRIMARY KEY,
        chat_name VARCHAR(255),
        user_id INT,
        documents JSON,
        conversation JSON,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    '''
    runsqlQuery(query)


def get_chat_info(user_id):
    try:
        query = '''
        SELECT chat_id, chat_name, documents, conversation
        FROM Chat_info
        WHERE user_id = %s
        '''
        result = runsqlQuery(query, (user_id,), fetch=True)

        if result:
            chat_info = {
                'chat_id': result[0][0],
                'chat_name': result[0][1],
                'documents': json.loads(result[0][2]) if result[0][2] else [],
                'conversation': json.loads(result[0][3]) if result[0][3] else []
            }
            return chat_info
        else:
            return None

    except Exception as e:
        print(f"Error in get_chat_info: {e}")
        return None


def get_question_list(user_id):
    try:
        query = '''
        SELECT id, question_text, embeddings_json
        FROM questions_list
        WHERE user_id = %s
        '''
        result = runsqlQuery(query, (user_id,), fetch=True)

        question_list = []
        for row in result:
            question_info = {
                'id': row[0],
                'question_text': row[1],
                'embeddings_json': row[2]
            }
            question_list.append(question_info)

        return question_list

    except Exception as e:
        print(f"Error in get_question_list: {e}")
        return None


def get_file_list():
    try:
        query = '''
        SELECT id, file_name, text_json, embeddings_json, user_id
        FROM file_data
        '''
        result = runsqlQuery(query, fetch=True)

        file_list = []
        for row in result:
            file_info = {
                'id': row[0],
                'file_name': row[1],
                'text_json': row[2],
                'embeddings_json': row[3],
                'user_id': row[4]
            }
            file_list.append(file_info)

        return file_list

    except Exception as e:
        print(f"Error: {e}")
        return None


def create_tables():
    create_users_table()
    create_file_data_table()
    create_questions_list_table()
    create_chat_info_table()


if __name__ == "__main__":
    create_tables()

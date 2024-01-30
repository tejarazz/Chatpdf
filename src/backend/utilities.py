from numpy.linalg import norm
import numpy as np
import fitz  # PyMuPDF
import mysql.connector
from config import Config
from langchain.embeddings import HuggingFaceEmbeddings
from typing import List
import openai
import os

openai.api_key = os.environ.get("OPENAI_API")

# Modules


def getResponseFromMessages(messages):

    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages)
#     print(chat_completion)
    bot_response = chat_completion.choices[0].message.content
    print(bot_response)
    return bot_response


def getSQLConnection():
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )

        if connection.is_connected():
            print("Connected to MySQL database")
            return connection

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return None


def runSelectQuery(query):
    results = None
    try:
        with getSQLConnection() as connection:
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    results = cursor.fetchall()
            else:
                raise Exception("Failed to connect to MySQL")
    except Exception as e:
        print(f'Some error occurred: {e}')
    return results


def runInsertQuery(query, values):
    try:
        last_inserted_id = None
        with getSQLConnection() as connection:
            if connection:
                with connection.cursor() as cursor:
                    # Ensure values is always treated as a tuple
                    cursor.execute(query, tuple(values))
                    last_inserted_id = cursor.lastrowid
                connection.commit()
                print("Insert successful")
            else:
                raise Exception("Failed to connect to MySQL")

    except Exception as e:
        print(f'Some error occurred: {e}')
        # Optionally, you may want to re-raise the exception to propagate it to the caller
        raise
    return last_inserted_id


def runUpdateQuery(query, values):
    try:
        with getSQLConnection() as connection:
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, values)
                connection.commit()
                print("Update successful")
            else:
                raise Exception("Failed to connect to MySQL")
    except Exception as e:
        print(f'Some error occurred: {e}')


def runDeleteQuery(query, values):
    try:
        connection = getSQLConnection()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
            connection.commit()
            print("Delete successful")
        else:
            raise Exception("Failed to connect to MySQL")
    except Exception as e:
        print(f'Some error occurred: {e}')
    finally:
        if connection:
            connection.close()


def runsqlQuery(query):
    try:
        connection = getSQLConnection()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
            connection.commit()
        else:
            raise Exception("Failed to connect to MySQL")
    except Exception as e:
        print(f'Some error occurred: {e}')
    finally:
        if connection:
            connection.close()

# read pdf


def read_pdf(file_path):
    # Open the PDF file
    pdf_document = fitz.open(file_path)

    # Initialize the output dictionary
    output = {}

    # Iterate through each page and extract text
    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        text = page.get_text()
        output[page_number] = text

    # Close the PDF file
    pdf_document.close()

    return output


def get_text_embeddings(text_dict: dict) -> dict:
    """
    Get embeddings for a dictionary of text using HuggingFaceEmbeddings.

    Parameters:
    - text_dict: dict, a dictionary where keys are document names and values are text content

    Returns:
    - embeddings_dict: dict, a dictionary where keys are document names and values are embeddings
    """
    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    texts = list(text_dict.values())
    embeddings = hf.embed_documents(texts)

    # Ensure that each embedding is converted to a list
    embeddings_dict = {key: embedding if isinstance(embedding, list) else embedding.tolist()
                       for key, embedding in zip(text_dict.keys(), embeddings)}
    return embeddings_dict


def get_embeddings_of_text(text: str) -> List[float]:
    """
    Get embeddings for a single text using HuggingFaceEmbeddings.

    Parameters:
    - text: str, input text for which embeddings are needed

    Returns:
    - embeddings: List[float], embeddings for the input text
    """
    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    embedding = hf.embed_query(text)
    return embedding


def cosine_similarity(embedding1, embedding2):
    """
    Calculate cosine similarity between two embeddings.

    Parameters:
    - embedding1: numpy array, the first embedding vector
    - embedding2: numpy array, the second embedding vector

    Returns:
    - similarity: float, cosine similarity between the two embeddings
    """
    dot_product = np.dot(embedding1, embedding2)
    norm_embedding1 = norm(embedding1)
    norm_embedding2 = norm(embedding2)

    similarity = dot_product / (norm_embedding1 * norm_embedding2)
    return similarity

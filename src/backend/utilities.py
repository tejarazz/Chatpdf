from numpy.linalg import norm
import numpy as np
import fitz  # PyMuPDF
import mysql.connector
from config import Config
from transformers import AutoTokenizer, AutoModel
import torch
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


def get_text_embeddings(text_dict):

    # Load pre-trained BERT tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    model = AutoModel.from_pretrained("bert-base-uncased")

    # Tokenize all input texts
    inputs = tokenizer(list(text_dict.values()), return_tensors="pt",
                       padding=True, truncation=True, max_length=512)

    # Forward pass through the BERT model
    with torch.no_grad():
        outputs = model(**inputs)

    # Extract the embeddings from the last layer (CLS token)
    embeddings = outputs.last_hidden_state.mean(dim=1).numpy()

    # Store the embeddings in the dictionary
    embeddings_dict = {key: embedding.tolist() for key,
                       embedding in zip(text_dict.keys(), embeddings)}

    return embeddings_dict


def get_embeddings_of_text(text, model_name="bert-base-uncased"):
    """
    Get BERT embeddings for a given text.

    Parameters:
    - text: str, input text for which embeddings are needed
    - model_name: str, BERT model name (default: "bert-base-uncased")

    Returns:
    - embeddings: torch.Tensor, contextualized embeddings for each token in the input text
    """
    # Load BERT model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    # Tokenize input text
    tokens = tokenizer(text, return_tensors='pt')

    # Forward pass through the BERT model
    with torch.no_grad():
        outputs = model(**tokens)

    # Extract embeddings from the last layer
    embeddings = outputs.last_hidden_state.squeeze(0)

    # You can use the mean pooling or any other pooling strategy if needed
    # Apply mean pooling along the sequence length dimension
    mean_pooling = torch.mean(embeddings, dim=1)

    return mean_pooling.numpy()


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


# def get_q_text_embeddings(text_input):
#     # Load pre-trained BERT tokenizer and model
#     tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
#     model = AutoModel.from_pretrained("bert-base-uncased")

#     # Check if the input is a single text or a dictionary of texts
#     if isinstance(text_input, str):
#         # If it's a single text, tokenize and process it
#         inputs = tokenizer(text_input, return_tensors="pt",
#                            padding=True, truncation=True, max_length=512)
#     elif isinstance(text_input, dict):
#         # If it's a dictionary, tokenize and process each text
#         inputs = tokenizer(list(text_input.values()), return_tensors="pt",
#                            padding=True, truncation=True, max_length=512)
#     else:
#         raise ValueError(
#             "Unsupported input type. Please provide a single text or a dictionary of texts.")

#     # Forward pass through the BERT model
#     with torch.no_grad():
#         outputs = model(**inputs)

#     # Extract the embeddings from the last layer (CLS token)
#     embeddings = outputs.last_hidden_state.mean(dim=1).numpy()

#     if isinstance(text_input, str):
#         # Return a list instead of an array for a single text
#         return embeddings[0].tolist()
#     elif isinstance(text_input, dict):
#         # Store the embeddings in the dictionary
#         embeddings_dict = {key: embedding.tolist()
#                            for key, embedding in zip(text_input.keys(), embeddings)}
#         return embeddings_dict

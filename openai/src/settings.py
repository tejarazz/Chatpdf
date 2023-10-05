import os

OPENAI_API_KEY = os.environ.get("OPENAI_API")

if OPENAI_API_KEY is None:
    raise ValueError("OpenAI API key not found in environment variable")

base_path = os.getcwd()
temp_path = os.path.join(base_path, 'temp')
print(temp_path)

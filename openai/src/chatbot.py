import os
import openai
from settings import OPENAI_API_KEY, temp_path
from utilities import write_to_pickle, read_from_pickle

# Config
openai.api_key = OPENAI_API_KEY

# Modules
def getResponseFromMessages(messages, query):
    messages.append({
        "role": "user",
        "content": query
      })
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages = messages)
#     print(chat_completion)
    bot_response = chat_completion.choices[0].message.content
    return bot_response

def getResponseFromInfo(prompt):
    completion = openai.Completion.create(model="text-curie-001", prompt = prompt, max_tokens = 100)
    # .create(,messages = messages)
    print(completion)
    bot_response = completion.choices[0].text
    return bot_response

class ConversationBuilder:
    def __init__(self, messages = []):
        self.messages = messages
        
    def askQuestion(self,question):
        answer = getResponseFromMessages(self.messages, question)
        self.messages.append({'role':'assistant', 'content':answer})
    def fetchConversation(self):
        return self.messages

def getCB():
    """
    returns conversation builder object. if the object is not present in specified path, it recreates it.
    """
    if not os.path.exists(temp_path):
        raise Exception(f'Check Temp Path! {temp_path}')
    
    CB_path = os.path.join(temp_path, 'CB.pkl')
    if not os.path.exists(CB_path):
        print('Reading CB failed. refreshing the CB Object')
        cb = ConversationBuilder()
        saveCB(cb)
    
    cb_reloaded = read_from_pickle(CB_path)

    return cb_reloaded

def saveCB(cb_obj):
    if not os.path.exists(temp_path):
        raise Exception(f'Check Temp Path! {temp_path}')
    
    CB_path = os.path.join(temp_path, 'CB.pkl')
    write_to_pickle(cb_obj, CB_path)
    print('Wrote to CB successfully!')
    
def resetCB():
    if not os.path.exists(temp_path):
        raise Exception(f'Check Temp Path! {temp_path}')
    
    CB_path = os.path.join(temp_path, 'CB.pkl')
    if os.path.exists(CB_path):
        os.remove(CB_path)
        print('CB reset Successfully')
    return None
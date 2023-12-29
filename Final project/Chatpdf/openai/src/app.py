import os
from flask import Flask, render_template, request, jsonify

from chatbot import getCB, saveCB, resetCB

from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)


@app.route('/')
def openaiTest():
    return render_template('openai_test.html', params={'username': 'Teja'})


@app.route('/ask_question', methods=['POST'])
def get_answer():
    question = request.form['question']

    # Fetch Answer from Chatbot
    CB = getCB()
    CB.askQuestion(question)
    saveCB(CB)
    conversation_list = CB.fetchConversation()

    response_html = ''
    # response_html += ''.join([f'<p><b>{message["role"]}:</b>&nbsp;{message["content"]}</p>' for message in conversation_list[-1:]])
    response_html += ''.join(
        [f'<p><b>{message["role"]}:</b>&nbsp;{message["content"]}</p>' for message in conversation_list])

    return jsonify({'answer': response_html})


@app.route('/getHistoricalConversation', methods=['GET'])
def getHistoricalConversation():

    # Fetch Answer from Chatbot
    CB = getCB()
    conversation_list = CB.fetchConversation()

    response_html = ''
    # response_html += ''.join([f'<p><b>{message["role"]}:</b>&nbsp;{message["content"]}</p>' for message in conversation_list[-1:]])
    response_html += ''.join(
        [f'<p><b>{message["role"]}:</b>&nbsp;{message["content"]}</p>' for message in conversation_list])

    return jsonify({'answer': response_html})


@app.route('/resetConversation', methods=['GET'])
def resetConversation():
    resetCB()
    return jsonify({'status message': 'success'})


if __name__ == '__main__':
    app.run(port=8080, debug=True)

from flask import Flask, render_template

from flask_cors import CORS
import os

app = Flask(__name__, static_folder='static')
CORS(app)
backend_base_path = os.getenv('BACKEND_BASE_PATH', 'http://127.0.0.1:5000/')


@app.route('/')
def openaiTest():
    return render_template('openai_test.html', params={'username': 'Teja', 'backend_base_path': backend_base_path})

@app.route('/loginpage.html')
def loginpage():
    return render_template('loginpage.html')

if __name__ == '__main__':
    app.run(port=8080, debug=True)

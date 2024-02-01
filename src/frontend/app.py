from flask import Flask, render_template

from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)


@app.route('/')
def openaiTest():
    return render_template('openai_test.html', params={'username': 'Teja'})


if __name__ == '__main__':
    app.run(port=8080, debug=True)

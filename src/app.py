"""
Can start the app with this command: flask --debug --app src/app.py run

Can also set environment variable:
export FLASK_APP=src/app.py
flask run
"""

from flask import Flask


app = Flask(__name__)

@app.route('/')
def get_root():
    return "<h1>Hello</h1>", 200

@app.route('/test')
def test():
    return {'test': "test is json"}, 200

@app.route('/testpost', methods=['POST'])
def test_post():
    return {'test post': 'this is a test'}, 200

@app.route('/param/<int:num>')
def test_param(num):
    return {'your param was': num}
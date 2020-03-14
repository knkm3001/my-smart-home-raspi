
import json
import requests
from flask import Flask, request, jsonify, render_template
from modules import funcs

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/')
def home():
    return 'raspiのさーばだよ'




@app.route('/api/infrared_code/',methods=["POST"])
def infrared_code():
    post_data = request.get_json()
    funcs.exec_infrared_code(post_data)
    return 'ok'


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
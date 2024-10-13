from flask import Flask , request , abort
import requests
import json
from Project.Config import *
import base64
from io import BytesIO
from bs4 import BeautifulSoup
from utils.askGPT import askGPT

app = Flask(__name__)

@app.route('/webhook', methods=['POST','GET'])
def webhook():
    if request.method == 'POST':
        payload = request.json

        print(payload)

        reply_token = payload['events'][0]['replyToken']
        message = payload['events'][0]['message']['text']
        response = askGPT(message)
        print(response)
        ReplyMessage(reply_token, response['output'])
        return request.json, 200

    else:
        abort(400)

def ReplyMessage(reply_token,response):
    LINE_API = 'https://api.line.me/v2/bot/message/reply'

    Authorization = 'Bearer {}'.format(channel_access_token)
    
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': Authorization
    }

    data = {
        "replyToken":reply_token,
        "messages":[{
              "type": "text",
              "text": response
        }]}

    data = json.dumps(data)
    r = requests.post(LINE_API, headers=headers, data=data)

    return 200

@app.route('/')
def hello():
    return "<marquee>IT'S WORKING</marquee>",200

if __name__ == "__main__":
    app.run(debug=True)
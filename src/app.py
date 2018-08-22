from flask import Flask, request
import json
import base64
import hashlib
import hmac
import socket
from config import consumer_secret, server_port

application = Flask('twitter-aaapi-bot')

def sign(msg):
    consumer_secret = consumer_secret.encode()
    if type(msg) == str:
        msg = msg.encode()

    sha256_hash_digest = hmac.new(consumer_secret, msg = msg, digestmod = hashlib.sha256).digest()

    return 'sha256=' + base64.b64encode(sha256_hash_digest).decode()

def validate(signature, data):
    return hmac.compare_digest(signature, sign(data))

@application.route('/twitter', methods = ['GET'])
def crc():
    if 'crc_token' in request.args and len(request.args.get('crc_token')) == 48:
        response_token = sign(request.args.get('crc_token'))
        response = {'response_token': response_token}

        return json.dumps(response), 200, {'Content-Type': 'application/json'}

    return 'No Content', 204, {'Content-Type': 'text/plain'}

@application.route('/twitter', methods = ['POST'])
def send_data():
    if 'X-Twitter-Webhooks-Signature' in request.headers:
        if signer.validate(request.headers.get('X-Twitter-Webhooks-Signature'), request.data):
            with socket.socket() as s:
                s.connect(('localhost', server_port))
                s.send(request.data)

            return 'OK', 200, {'Content-Type': 'text/plain'}

    return 'No Content', 204, {'Content-Type': 'text/plain'}


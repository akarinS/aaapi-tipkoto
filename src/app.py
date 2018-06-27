from flask import Flask, request
from signature import Signature
from config import consumer_key, consumer_secret, access_token, access_token_secret
from config import rpc_user, rpc_password, rpc_port
from tipkoto import TipKoto
from threading import Thread
import json

application = Flask('twitter-aaapi-bot')
signer = Signature(consumer_secret)

@application.route('/twitter', methods = ['GET'])
def get():
    if 'crc_token' in request.args and len(request.args.get('crc_token')) == 48:
        response_token = signer.get_response_token(request.args.get('crc_token').encode())
        response = {'response_token': response_token}

        return json.dumps(response), 200, {'Content-Type': 'application/json'}

    return 'No Content', 204, {'Content-Type': 'text/plain'}

@application.route('/twitter', methods = ['POST'])
def post():
    if 'X-Twitter-Webhooks-Signature' in request.headers:
        if signer.validate(request.headers.get('X-Twitter-Webhooks-Signature'), request.data):
            data = request.json

            bot = TipKoto(consumer_key, consumer_secret, access_token, access_token_secret, rpc_user, rpc_password, rpc_port)
            thread = Thread(target = bot.run, args = (data,))
            thread.start()

            return 'OK', 200, {'Content-Type': 'text/plain'}

    return 'No Content', 204, {'Content-Type': 'text/plain'}


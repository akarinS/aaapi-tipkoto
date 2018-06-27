import base64
import hashlib
import hmac

class Signature(object):

    def __init__(self, consumer_secret):
        self.consumer_secret = consumer_secret.encode()

    def _sign(self, msg):   # msg must be "<class 'bytes'>"
        sha256_hash_digest = hmac.new(self.consumer_secret, msg = msg, digestmod = hashlib.sha256).digest()
        return 'sha256=' + base64.b64encode(sha256_hash_digest).decode()

    def get_response_token(self, crc_token):
        return self._sign(crc_token)

    def validate(self, x_twitter_webhooks_signature, data):
        return hmac.compare_digest(x_twitter_webhooks_signature, self._sign(data))


from requests_oauthlib import OAuth1Session

class Twittle(object):

    def __init__(self,
                 consumer_key, consumer_secret
                 access_token, access_token_secret):
        self.twitter = OAuth1Session(consumer_key, consumer_secret,
                                     access_token, access_token_secret)

    def tweet(self, status, in_reply_to_status_id = None):
        params = {'status': status}
        if in_reply_to_status_id is not None:
            params['in_reply_to_status_id'] = in_reply_to_status_id

        response = self.twitter.post('https://api.twitter.com/1.1/statuses/update.json',
                                     params = params)

        return response

    def dm(self, text, recipient_id):
        request_data = {'event': {'type': 'message_create',
                                  'message_create': {'target': {'recipient_id': recipient_id},
                                                     'message_data': {'text': text}}}}

        response = self.twitter.post('https://api.twitter.com/1.1/direct_messages/events/new.json',
                                     json = request_data)
        
        return response

    def user(self, screen_name):
        response = self.twitter.get('https://api.twitter.com/1.1/users/show.json',
                                    params = {'screen_name': screen_name})

        return response

    def follow(self, user_id):
        response = self.twitter.post('https://api.twitter.com/1.1/friendships/create.json',
                                     params = {'user_id': user_id, 'follow': 'true'})

        return response


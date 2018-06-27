class BaseAAAPI(object):

    def run(self, data):
        if 'tweet_create_events' in data:
            self.tweet_create_events(data)

        elif 'favorite_events' in data:
            self.favorite_events(data)

        elif 'follow_events' in data:
            self.follow_events(data)

        elif 'block_events' in data:
            self.block_events(data)

        elif 'mute_events' in data:
            self.mute_events(data)

        elif 'user_event' in data:
            self.user_event(data)

        elif 'direct_message_events' in data:
            self.direct_message_events(data)

        elif 'direct_message_indicate_typing_events' in data:
            self.direct_message_indicate_typing_events(data)

        elif 'direct_message_mark_read_events' in data:
            self.direct_message_mark_read_events(data)

    def tweet_create_events(self, data):
        pass

    def favorite_events(self, data):
        pass

    def follow_events(self, data):
        pass

    def block_events(self, data):
        pass

    def mute_events(self, data):
        pass

    def user_event(self, data):
        pass

    def direct_message_events(self, data):
        pass

    def direct_message_indicate_typing_events(self, data):
        pass

    def direct_message_mark_read_events(self, data):
        pass


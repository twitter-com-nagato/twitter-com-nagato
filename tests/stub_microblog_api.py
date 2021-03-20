from microblog import microblog_api
from microblog import microblog_user


class StubMicroblogApi(microblog_api.MicroblogApi):
    def __init__(self):
        self.me = microblog_user.MicroblogUser(15498, 'nagato')
        self.follower_ids = set()
        self.friend_ids = set()
        self.pending_friend_ids = set()
        self.blocking_ids = {100, 200}
        self.posts = []
        self.home_statuses = []
        self.user_statuses = {}
        self.replies = []
        self.sent_messages = []

    def verify_credentials(self):
        return self.me

    def get_home_statuses(self):
        return self.home_statuses

    def get_user_statuses(self, user_id, max_id=None):
        return self.user_statuses[user_id]

    def get_replies(self, since_id=None):
        return self.replies

    def get_received_messages(self, since_id):
        return []

    def get_sent_messages(self):
        return []

    def get_follower_ids(self):
        return self.follower_ids

    def get_friend_ids(self):
        return self.friend_ids

    def get_pending_friend_ids(self):
        return set()

    def delete_message(self, message_id):
        pass

    def follow(self, user_id):
        self.friend_ids.add(user_id)

    def remove(self, user_id):
        self.friend_ids.remove(user_id)

    def block(self, user_id):
        self.blocking_ids.add(user_id)

    def unblock(self, user_id):
        self.blocking_ids.remove(user_id)

    def post(self, text, url=None, in_reply_to=None):
        pass

    def send(self, text, user_id):
        pass

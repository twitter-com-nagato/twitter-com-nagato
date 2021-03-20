from mastodon import Mastodon
from .mastodon_user import MastodonUser
from .microblog_api import MicroblogApi
from .mastodon_status import Toot


class MastodonApi(MicroblogApi):
    def __init__(self, access_token, api_base_url):
        assert access_token, 'The access token is mandatory but not set.'
        assert api_base_url, 'The API base URL is mandatory but not set.'
        self.mastodon = Mastodon(access_token=access_token, api_base_url=api_base_url, ratelimit_method='throw')
        self.credential = MastodonUser(self.mastodon.account_verify_credentials())

    def verify_credentials(self):
        return self.credential

    def get_home_statuses(self):
        return [Toot(toot) for toot in self.mastodon.timeline_home()]

    def get_user_statuses(self, user_id, max_id=None):
        return [Toot(toot) for toot in self.mastodon.account_statuses(user_id, max_id=max_id)]

    def get_replies(self, since_id=None):
        # since_id cannot be passed to notifications API because it accepts an notification ID,
        # which is different from a toot ID.
        # Therefore, retrieve all notifications first then filter them based on the status ID.
        return [Toot(notification.status)
                for notification
                in self.mastodon.notifications()
                if notification.type == 'mention' and notification.status.id >= since_id]

    def get_received_messages(self, since_id):
        return []

    def get_sent_messages(self):
        return []

    def get_follower_ids(self):
        return set([follower.id for follower in self.mastodon.account_followers(self.credential.id)])

    def get_friend_ids(self):
        return set([followee.id for followee in self.mastodon.account_following(self.credential.id)])

    def get_pending_friend_ids(self):
        return set([])

    def delete_message(self, message_id):
        pass

    def follow(self, user_id):
        self.mastodon.account_follow(user_id)

    def remove(self, user_id):
        self.mastodon.account_unfollow(user_id)

    def block(self, user_id):
        self.mastodon.account_block(user_id)

    def unblock(self, user_id):
        self.mastdon.account_unblock(user_id)

    def post(self, text, url=None, in_reply_to=None):
        text = (text + '\n' + url) if url else text
        if in_reply_to:
            self.mastodon.status_reply(in_reply_to.dict, text)
        else:
            self.mastodon.status_post(text, visibility='unlisted')

    def send(self, text, user_id):
        pass

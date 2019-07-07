import twitter
from . import microblog_api
from . import twitter_user
from .twitter_status import Tweet


def compose(status, max_length, screen_name=None, url=None):
    """
    Composes the status message with a screen name to reply and a URI (if any).
    The status will be truncated with '...' if it exceeds the character limit
    (280 ASCII characters as of 2018-07-01).
    """

    if not status:
        return None

    max_length = 280
    expected_length = max_length + 1
    cut_length = 0
    while expected_length > max_length:
        composed_status = ''

        if screen_name:
            composed_status += '@' + screen_name + ' '

        if cut_length > 0:
            composed_status += status[:len(status) - cut_length] + '...'
        else:
            composed_status += status

        if url:
            composed_status += ' ' + url

        expected_length = twitter.twitter_utils.calc_expected_status_length(
            composed_status)
        cut_length += expected_length - max_length

    return composed_status


def get_id(tweet):
    """
    Gets the ID of the specified tweet.
    """
    return int(tweet._json['id_str'])


def get_tweets(tweets):
    """
    Gets a list of Tweet instances from a list of dicts.
    """
    return [Tweet(tweet) for tweet in tweets]


class TwitterApi(microblog_api.MicroblogApi):
    def __init__(
            self,
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret):
        assert consumer_key, 'The consumer key is mandatory but not set.'
        assert consumer_secret, 'The consumer secret is mandatory but not set.'
        assert access_token, 'The access token is mandatory but not set.'
        assert access_token_secret, 'The access token secret is mandatory but not set.'
        self.twitter = twitter.Api(
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret)

    def get_error_message(self, e):
        message = '"'
        message += '", "'.join([str(message) for message in e.message])
        message += '"\n'
        message += str(vars(self.twitter.rate_limit))
        return message

    def verify_credentials(self):
        return twitter_user.TwitterUser(self.twitter.VerifyCredentials())

    def get_home_statuses(self):
        try:
            return get_tweets(self.twitter.GetHomeTimeline(count=200))
        except twitter.error.TwitterError as e:
            raise Exception(self.get_error_message(e))

    def get_user_statuses(self, user_id, max_id=None):
        try:
            return get_tweets(self.twitter.GetUserTimeline(user_id=user_id, max_id=max_id, count=200))
        except twitter.error.TwitterError as e:
            raise Exception(self.get_error_message(e))

    def get_replies(self, since_id=None):
        try:
            return get_tweets(self.twitter.GetMentions(since_id=since_id))
        except twitter.error.TwitterError as e:
            raise Exception(self.get_error_message(e))

    def get_received_messages(self, since_id):
        # python-twitter hasn't followed changes
        # in Twitter direct message APIs as of Sep. 22, 2018.
        # Disable direct message interactions until the library gets updated.
        return []

    def get_sent_messages(self):
        # python-twitter hasn't followed changes
        # in Twitter direct message APIs as of Sep. 22, 2018.
        # Disable direct message interactions until the library gets updated.
        return []

    def get_follower_ids(self):
        try:
            return set(self.twitter.GetFollowerIDs(count=5000))
        except twitter.error.TwitterError as e:
            raise Exception(self.get_error_message(e))

    def get_friend_ids(self):
        try:
            return set(self.twitter.GetFriendIDs(count=5000))
        except twitter.error.TwitterError as e:
            raise Exception(self.get_error_message(e))

    def get_pending_friend_ids(self):
        try:
            return set(self.twitter.OutgoingFriendship())
        except twitter.error.TwitterError as e:
            raise Exception(self.get_error_message(e))

    def delete_message(self, message_id):
        # python-twitter hasn't followed changes
        # in Twitter direct message APIs as of Sep. 22, 2018.
        # Disable direct message interactions until the library gets updated.
        pass

    def follow(self, user_id):
        try:
            self.twitter.CreateFriendship(user_id)
        except twitter.error.TwitterError as e:
            raise Exception(self.get_error_message(e))

    def remove(self, user_id):
        try:
            self.twitter.DestroyFriendship(user_id)
        except twitter.error.TwitterError as e:
            raise Exception(self.get_error_message(e))

    def block(self, user_id):
        try:
            self.twitter.CreateBlock(user_id=user_id)
        except twitter.error.TwitterError as e:
            raise Exception(self.get_error_message(e))

    def unblock(self, user_id):
        try:
            self.twitter.DestroyBlock(user_id=user_id)
        except twitter.error.TwitterError as e:
            raise Exception(self.get_error_message(e))

    def post(self, text, url=None, in_reply_to=None):
        try:
            if in_reply_to:
                text = compose(text, 280, in_reply_to.user.screen_name, url)
                self.twitter.PostUpdate(text, in_reply_to_status_id=in_reply_to.id)
            else:
                text = compose(text, 280, None, url)
                self.twitter.PostUpdate(text)
        except twitter.error.TwitterError as e:
            raise Exception(self.get_error_message(e))

    def send(self, text, user_id):
        # python-twitter hasn't followed changes
        # in Twitter direct message APIs as of Sep. 22, 2018.
        # Disable direct message interactions until the library gets updated.
        pass

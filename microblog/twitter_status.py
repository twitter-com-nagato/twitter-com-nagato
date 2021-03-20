import datetime
import pytz
from . import microblog_status
from . import twitter_user


class Tweet(microblog_status.MicroblogStatus):
    """
    A class which represents a tweet or a message on Twitter.
    """

    def __init__(self, tweet_object):
        """
        Initializes a new Tweet instance from a Tweet object.
        Cf. https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object.html
        """

        super().__init__(
            id=tweet_object.id,
            text=tweet_object.text,
            user=twitter_user.TwitterUser(tweet_object.user),
            created_at=datetime.datetime.fromtimestamp(
                tweet_object.created_at_in_seconds,
                tz=pytz.timezone('Asia/Tokyo')),
            in_reply_to_status_id=tweet_object.in_reply_to_status_id,
            in_reply_to_user_id=tweet_object.in_reply_to_user_id)

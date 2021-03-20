from . import microblog_user


class TwitterUser(microblog_user.MicroblogUser):
    def __init__(self, user_object):
        """
        Initializes a new instance of TwitterUser class from a User object.
        Cf. https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/user-object
        """

        super().__init__(
            id=user_object.id,
            screen_name=user_object.screen_name)

from . import microblog_user


class MastodonUser(microblog_user.User):
    def __init__(self, user_dict):
        """
        Initializes a new instance of MastodonUser class from a user dict.
        Cf. https://mastodonpy.readthedocs.io/en/stable/#user-dict
        """

        super().__init__(
            id=user_dict.id,
            screen_name=user_dict.username)

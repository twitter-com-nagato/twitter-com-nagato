from . import mastodon_user
from . import microblog_status


class Toot(microblog_status.MicroblogStatus):
    """
    A class which represents a toot on Mastodon.
    """

    def __init__(self, toot_dict):
        """
        Initializes a new Toot instance from a toot dict.
        Cf. https://mastodonpy.readthedocs.io/en/stable/#toot-dicts
        """

        super().__init__(
            id=toot_dict.id,
            text=toot_dict.content,
            user=mastodon_user.MastodonUser(toot_dict.account),
            created_at=toot_dict.created_at,
            in_reply_to_status_id=toot_dict.in_reply_to_id,
            in_reply_to_user_id=toot_dict.in_reply_to_account_id)

        self.dict = toot_dict

import datetime
from . import microblog_user


class MicroblogStatus(object):
    def __init__(
            self,
            id: str,
            text: str,
            user: microblog_user.MicroblogUser,
            created_at: datetime.datetime,
            in_reply_to_status_id: str,
            in_reply_to_user_id: str):

        assert type(created_at) == datetime.datetime, 'created_at is not a datetime object.'

        self.id: str = id
        self.text: str = text
        self.user: MicroblogUser = user
        self.created_at: datetime.datetime = created_at
        self.in_reply_to_status_id: str = in_reply_to_status_id
        self.in_reply_to_user_id: str = in_reply_to_user_id

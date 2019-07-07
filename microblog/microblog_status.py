import datetime
from abc import ABC


class Status(ABC):
    def __init__(self, id, text, user, created_at, in_reply_to_status_id, in_reply_to_user_id):
        assert type(created_at) == datetime.datetime, 'created_at is not a datetime object.'

        self.id = id
        self.text = text
        self.user = user
        self.created_at = created_at
        self.in_reply_to_status_id = in_reply_to_status_id
        self.in_reply_to_user_id = in_reply_to_user_id

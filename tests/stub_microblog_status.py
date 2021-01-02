from . import microblog_status


class StubMicroblogStatus(microblog_status.Status):
    def __init__(self, id, text, user, created_at, in_reply_to_status_id, in_reply_to_user_id):
        super().__init__(
            id=id,
            text=text,
            user=user,
            created_at=created_at,
            in_reply_to_status_id=in_reply_to_status_id,
            in_reply_to_user_id=in_reply_to_user_id)

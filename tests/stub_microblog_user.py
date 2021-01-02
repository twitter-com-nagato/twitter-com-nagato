from . import microblog_user


class StubMicroblogUser(microblog_user.User):
    def __init__(self, id, screen_name):
        super().__init__(id=id, screen_name=screen_name)

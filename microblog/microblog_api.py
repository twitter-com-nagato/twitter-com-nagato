#!/usr/bin/env python3

from abc import ABC
from abc import abstractmethod


class MicroblogApi(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def verify_credentials(self):
        pass

    @abstractmethod
    def get_home_statuses(self):
        pass

    @abstractmethod
    def get_user_statuses(self, user_id, max_id=None):
        pass

    @abstractmethod
    def get_replies(self, since_id=None):
        pass

    @abstractmethod
    def get_follower_ids(self):
        pass

    @abstractmethod
    def get_friend_ids(self):
        pass

    @abstractmethod
    def get_received_messages(self, since_id):
        pass

    @abstractmethod
    def get_sent_messages(self):
        pass

    @abstractmethod
    def get_pending_friend_ids(self):
        pass

    @abstractmethod
    def delete_message(self, message_id):
        pass

    @abstractmethod
    def follow(self, user_id):
        pass

    @abstractmethod
    def remove(self, user_id):
        pass

    @abstractmethod
    def block(self, user_id):
        pass

    @abstractmethod
    def unblock(self, user_id):
        pass

    @abstractmethod
    def post(self, text, url=None, in_reply_to=None):
        pass

    @abstractmethod
    def send(self, text, user_id):
        pass

from .stub_book_search import StubBookSearch
from .stub_keyword_extraction import StubKeywordExtraction
from .stub_microblog_api import StubMicroblogApi
from microblog import microblog_status
from microblog import microblog_user
import datetime
import logging
import nagato
import unittest


class NagatoTest(unittest.TestCase):
    def setUp(self):
        self.microblog = StubMicroblogApi()
        self.book_search = StubBookSearch()
        self.keyphrase_extraction = StubKeywordExtraction()
        self.nagato = nagato.Nagato( self.microblog, self.book_search, self.keyphrase_extraction)

        logger = logging.getLogger('nagato')
        logger.handlers = []
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    def test_refollow(self):
        self.nagato.microblog.follower_ids = {2, 4, 6, 8, 10, 12, 14, 16}
        self.nagato.microblog.friend_ids = {3, 6, 9, 12, 15}
        self.nagato.refollow()
        self.assertEqual({2, 4, 6, 8, 10, 12, 14, 16}, self.nagato.microblog.follower_ids)

    def test_book_recommendation(self):
        user = microblog_user.MicroblogUser(15498, 'nagato')
        status: type = microblog_status.MicroblogStatus
        created_at: type = datetime.datetime
        self.microblog.user_statuses[15498] = [
            status('4', 'Nagato is cute.', user, created_at(2021, 1, 1, 10, 0, 0), None, None),
            status('3', 'She is Nagato.', user, created_at(2021, 1, 1, 9, 0, 0), None, None),
            status('2', 'Do you know Nagato?', user, created_at(2021, 1, 1, 8, 0, 0), None, None),
            status('1', 'How cute she is!', user, created_at(2021, 1, 1, 7, 0, 0), None, None),
        ]

        (response_text, response_url) = self.nagato.getResponse(15498, 'お勧めの本は？')
        self.assertEqual('Cute nagato book', response_text)
        self.assertEqual('https://www.example.com/#cute_nagato_book', response_url)

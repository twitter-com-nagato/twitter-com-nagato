import nagato
import unittest
from .stub_book_search import StubBookSearch
from .stub_keyphrase_extraction import StubKeyphraseExtraction
from .stub_microblog_api import StubMicroblogApi


class NagatoTest(unittest.TestCase):
    def setUp(self):
        microblog = StubMicroblogApi()
        book_search = StubBookSearch()
        keyphrase_extraction = StubKeyphraseExtraction()
        self.nagato = nagato.Nagato(microblog, book_search, keyphrase_extraction)

    def test_refollow(self):
        self.nagato.microblog.follower_ids = {2, 4, 6, 8, 10, 12, 14, 16}
        self.nagato.microblog.friend_ids = {3, 6, 9, 12, 15}
        self.nagato.refollow()
        self.assertEqual({2, 4, 6, 8, 10, 12, 14, 16}, self.nagato.microblog.follower_ids)

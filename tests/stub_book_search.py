from book_search.book_search import BookSearch


class StubBookSearch(BookSearch):
    def search(self, queries):
        return []

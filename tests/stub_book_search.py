from book_search.book import Book
from book_search.book_search import BookSearch


class StubBookSearch(BookSearch):
    def search(self, queries):
        book = Book('Cute nagato book', 'https://www.example.com/#cute_nagato_book')
        return (book, 1)

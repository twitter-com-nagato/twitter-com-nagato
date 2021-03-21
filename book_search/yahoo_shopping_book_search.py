from .book import Book
from .book_search import BookSearch


class YahooShoppingBookSearch(BookSearch):
    def __init__(self, yapi):
        self.yapi = yapi

    def search(self, queries):
        api_url = 'https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch'
        response = self.yapi.api(api_url, {
            'query': ' '.join(queries),
            'genre_category_id': 10002,
            'results': 1,
        })

        if response:
            available_result_count = int(response['totalResultsAvailable'])
            returned_result_count = int(response['totalResultsReturned'])
            if returned_result_count:
                best_result = response['hits'][0]
                best_book = Book(best_result['name'], best_result['url'])
                return (best_book, available_result_count)

        return (None, 0)

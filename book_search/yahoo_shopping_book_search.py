from .book import Book
from .book_search import BookSearch


class YahooShoppingBookSearch(BookSearch):
    def __init__(self, yapi):
        self.yapi = yapi

    def search(self, queries):
        api_url = 'http://shopping.yahooapis.jp/ShoppingWebService/V1/json/itemSearch'
        response = self.yapi.api(api_url, {
            'query': ' '.join(queries),
            'category_id': 10002,
            'hits': 1,
        })

        if response:
            result_set = response['ResultSet']
            available_result_count = int(result_set['totalResultsAvailable'])
            returned_result_count = int(result_set['totalResultsReturned'])
            if returned_result_count:
                best_result = result_set['0']['Result']['0']
                best_book = Book(best_result['Name'], best_result['Url'])
                return (best_book, available_result_count)

        return (None, 0)

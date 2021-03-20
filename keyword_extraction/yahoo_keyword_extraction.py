from .keyword_extraction import KeywordExtraction


class YahooKeywordExtraction(KeywordExtraction):
    def __init__(self, yapi):
        self.yapi = yapi

    def extract(self, sentence):
        api_url = 'http://jlp.yahooapis.jp/KeyphraseService/V1/extract'
        response = self.yapi.api(api_url, {
            'output': 'json',
            'sentence': sentence,
        }, 'POST')

        if response:
            response = [k for k, v in sorted(response.items(), key=lambda x:x[1], reverse=True)]

        return response

from .keyword_extraction import KeywordExtraction


class StubKeywordExtraction(KeywordExtraction):
    def __init__(self, yapi):
        self.yapi = yapi

    def extract(self, sentence):
        return []

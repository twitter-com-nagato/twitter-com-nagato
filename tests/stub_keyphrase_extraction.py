from keyword_extraction.keyword_extraction import KeywordExtraction


class StubKeyphraseExtraction(KeywordExtraction):
    def extract(self, sentence):
        return []

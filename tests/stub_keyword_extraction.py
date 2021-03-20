from keyword_extraction import keyword_extraction
import collections
import re


class StubKeywordExtraction(keyword_extraction.KeywordExtraction):
    def extract(self, sentence):
        words = re.sub(r'[^A-Za-z ]', r'', sentence).split(' ')
        common_word_counts = collections.Counter(words).most_common()
        common_words = [common_word_count[0] for common_word_count in common_word_counts]
        return common_words

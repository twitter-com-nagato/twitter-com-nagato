from abc import ABC
from abc import abstractmethod


class KeywordExtraction(ABC):
    @abstractmethod
    def extract(self, sentence):
        pass

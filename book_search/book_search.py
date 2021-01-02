from abc import ABC
from abc import abstractmethod


class BookSearch(ABC):
    @abstractmethod
    def search(self, queries):
        pass

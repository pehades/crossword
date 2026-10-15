from abc import ABC, abstractmethod

from crossword.business_logic.models import SearchResult


class BaseSearch(ABC):

    @abstractmethod
    def search(self, query: str) -> list[SearchResult]:
        pass

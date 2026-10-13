from abc import ABC, abstractmethod

from pydantic import BaseModel


class SearchResult(BaseModel):
    id: str
    source: str
    title: str
    content: str


class BaseSearch(ABC):

    @abstractmethod
    def search(self, query: str) -> list[SearchResult]:
        pass

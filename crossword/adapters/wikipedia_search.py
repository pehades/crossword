from datetime import datetime

import requests
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel

from crossword.adapters.base_search import BaseSearch
from crossword.business_logic.models import SearchResult
from crossword.common.logger import create_logger

logger = create_logger(__name__)


class WikipediaPage(BaseModel):
    pageid: int
    title: str
    extract: str = ''
    contentmodel: str
    pagelanguage: str
    touched: datetime
    lastrevid: int
    length: int
    fullurl: str


class Wikipedia(BaseSearch):

    def __init__(self, url: str = "https://en.wikipedia.org/w/api.php", headers: dict | None = None):
        self.url = url
        self.headers = headers or {"User-Agent": "pet project"}

    def search(self, query: str) -> list[SearchResult]:
        return [
            SearchResult(
                id=f"wikipedia:{page.pageid}",
                url=page.fullurl,
                source='wikipedia',
                title=page.title,
                content=page.extract
            ) for page in self.get_pages_for_topic(query, srlimit=1)
        ]

    def get_pages_for_topic(self, searches: str | list[str], srlimit: int = 5) -> list[WikipediaPage]:

        if isinstance(searches, str):
            searches = [searches]

        with ThreadPoolExecutor(max_workers=1) as executor:
            topics = list(executor.map(lambda search: self.search_topic(search, srlimit=srlimit), searches))

        # overlapping searches return the same pages, keep each page once
        pages = {}
        for topic in topics:
            if not topic:
                continue
            for page in topic.json()['query']['search']:
                pages[page['pageid']] = page

        return list(self.get_pages(list(pages)).values())

    def search_topic(self, search: str, srlimit: int):
        import time
        params = {
            'action': 'query', 'list': 'search', 'srsearch': search, 'srlimit': srlimit, 'explaintext': 1, 'format': 'json'
        }
        for attempt in range(3):
            result = requests.get(url=self.url, headers=self.headers, params=params)
            if result.ok:
                break
            logger.warning(f"search_topic failed for {search}: {result.status_code} {result.reason} - {result.text[:500]}")
            time.sleep(2 ** attempt)
        if not result.ok:
            return []
        return result


    def get_page(self, pageids: str):
        import time
        params = {
            'action': 'query', 'prop': 'extracts|info', 'pageids': pageids, 'explaintext': 1, 'format': 'json',
            'inprop': 'url'
        }
        for attempt in range(3):
            result = requests.get(url=self.url, headers=self.headers, params=params)
            if result.ok:
                break
            logger.warning(f"get_page failed for pageid {pageids}: {result.status_code} {result.reason} - {result.text[:500]}")
            time.sleep(2 ** attempt)
        if not result.ok:
            return []
        return result

    def get_pages(self, pageids: list[int]) -> dict[int, WikipediaPage]:

        # with ThreadPoolExecutor(max_workers=1) as executor:
        #     responses = executor.map(self.get_page, pageids)
        responses = [self.get_page(pageid) for pageid in pageids]
        pages = {}
        for response in responses:
            if not response:
                continue
            for page in response.json()['query']['pages'].values():
                parsed_page = WikipediaPage.model_validate(page)
                pages[parsed_page.pageid] = parsed_page

        return pages
from tavily import TavilyClient

from crossword.adapters.base_search import BaseSearch, SearchResult


class WebSearchEngine(BaseSearch):

    def __init__(self, client: TavilyClient) -> None:
        self.client = client

    def search(self, query: str) -> list[SearchResult]:
        results = self.client.search(query, include_raw_content=True)['results']
        return [
            SearchResult(
                id=f'web_search:{result['url']}',
                url=result['url'],
                source='web',
                title=result['title'],
                # raw_content is the full page, fall back to the snippet when tavily couldn't extract it
                content=result.get('raw_content') or result['content']
            ) for result in results
        ]

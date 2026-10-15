import pytest

from crossword.adapters.base_search import SearchResult
from crossword.adapters.vector_db import VectorDB
from crossword.common.factories import AdaptersFactory


@pytest.fixture()
def vector_db() -> VectorDB:
    return AdaptersFactory.get_vector_db()


class TestVectorDB:

    def test_insert_and_query(self, vector_db):


        search_result = SearchResult(id='123', url='http://example.com', source='web',
                                     title='rag stuff', content='This is a document about RAG stuff')
        vector_db.insert([search_result])

        query_results = vector_db.query(query='rag info', result_ids=['123'])

        assert len(query_results) == 1
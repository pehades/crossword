import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter, TextSplitter
from sentence_transformers import CrossEncoder

from crossword.adapters.base_search import SearchResult


class VectorDB:

    def __init__(
            self,
            client: chromadb.ClientAPI,
            splitter: TextSplitter | None = None,
            reranker: CrossEncoder | None = None
    ):
        self.client = client
        self.collection = self.client.get_or_create_collection('search_results', metadata={"hnsw:space": "cosine"})

        self.splitter = splitter or RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        self.reranker = reranker or CrossEncoder('cross-encoder/ms-marco-MiniLM-L6-v2')

    def insert(self, results: list[SearchResult]) -> None:
        for result in results:
            if not self.is_indexed(result):
                self.index(result)

    def is_indexed(self, result: SearchResult) -> bool:
        return bool(self.collection.get(where={'result_id': result.id}, limit=1)['ids'])

    def index(self, result: SearchResult) -> None:
        chunks = self.splitter.split_text(result.content)
        if not chunks:
            return

        self.collection.add(
            ids=[f"{result.id}_{i}" for i in range(len(chunks))],
            documents=chunks,
            metadatas=[{'result_id': result.id, 'source': result.source} for _ in chunks]
        )

    def query(self, query: str, result_ids: list[str]) -> list[str]:
        """Return the chunks most relevant to the query, searching only within the given results."""
        if not result_ids:
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=20,
            where={'result_id': {'$in': result_ids}}
        )

        documents_with_relevancy_score = [
            {'query': query, 'document': d, 'score': float(self.reranker.predict((query, d)))}
            for d in results['documents'][0]
        ]

        sorted_documents = sorted(documents_with_relevancy_score, key=lambda x: x['score'], reverse=True)
        return [d['document'] for d in sorted_documents]

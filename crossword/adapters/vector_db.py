import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter, TextSplitter

from crossword.business_logic.models import DBDocument, SearchResult


class VectorDB:

    def __init__(
            self,
            client: chromadb.ClientAPI,
            splitter: TextSplitter | None = None,
            reranker=None
    ):
        self.client = client
        self.collection = self.client.get_or_create_collection('search_results', metadata={"hnsw:space": "cosine"})

        self.splitter = splitter or RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

        # This import takes time, so we only import it when we initialize VectorDB
        from sentence_transformers import CrossEncoder
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
            metadatas=[{'result_id': result.id, 'source': result.source, 'url': result.url, 'title': result.title}
                       for _ in chunks]
        )

    def query(self, query: str, result_ids: list[str]) -> list[DBDocument]:
        """Return the chunks most relevant to the query, searching only within the given results."""
        if not result_ids:
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=20,
            where={'result_id': {'$in': result_ids}}
        )

        documents_with_relevancy_score = [
            DBDocument.model_validate(
                {
                    'chunk_id': chunk_id,
                    'document_id': metadata['result_id'],
                    'url': metadata['url'],
                    'query': query,
                    'document': d,
                    'score': float(self.reranker.predict((query, d)))
                }
            ) for chunk_id, d, metadata in zip(results['ids'][0], results['documents'][0], results['metadatas'][0])
        ]

        return sorted(documents_with_relevancy_score, key=lambda x: x.score, reverse=True)

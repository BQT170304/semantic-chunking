from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from langchain_community.vectorstores import OpenSearchVectorSearch
from shared.logging import get_logger

logger = get_logger(__name__)


class OpenSearchRetriever:
    def __init__(self, index_name: str, opensearch_username: str, opensearch_password: str, bedrock_embeddings_client, opensearch_endpoint: str, is_aoss: bool = False):
        try:
            self.vectorstore = OpenSearchVectorSearch(
                index_name=index_name,
                embedding_function=bedrock_embeddings_client,
                opensearch_url=opensearch_endpoint,
                http_auth=(opensearch_username, opensearch_password),
                is_aoss=is_aoss,
            )
        except Exception as e:
            logger.error(f'Error initializing OpenSearch retriever: {str(e)}')
            raise

    def get_relevant_documents(self, query: str, k: int = 4, search_kwargs: Optional[Dict[str, Any]] = None) -> List:
        try:
            if not query.strip():
                return []

            search_kwargs = search_kwargs or {}
            hybrid = search_kwargs.pop('hybrid', False)
            filter = search_kwargs.pop('filter', None)

            if hybrid:
                # Hybrid search: combine semantic and keyword search
                docs_semantic = self.vectorstore.similarity_search(
                    query,
                    k=k,
                    boolean_filter=filter,
                    search_kwargs=search_kwargs,
                    vector_field='embedding_vector',
                    text_field='content',
                )
                docs_keyword = self.vectorstore.similarity_search(
                    query,
                    k=k,
                    boolean_filter=filter,
                    search_kwargs={**search_kwargs, 'use_keyword': True},
                    vector_field='embedding_vector',
                    text_field='content',
                )
                docs = docs_semantic + [doc for doc in docs_keyword if doc not in docs_semantic]
                docs = docs[:k]
            else:
                docs = self.vectorstore.similarity_search(
                    query,
                    k=k,
                    boolean_filter=filter,
                    search_kwargs=search_kwargs,
                    vector_field='embedding_vector',
                    text_field='content',
                )

            return docs
        except Exception as e:
            logger.error(f'Error retrieving documents: {str(e)}')
            return []  # Return empty list instead of raising exception

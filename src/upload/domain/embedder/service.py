from __future__ import annotations

import json
import time
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from typing import Dict
from typing import List

import boto3
from config import INDEX_NAME
from config import logger
from config import MAX_WORKERS
from config import OPENSEARCH_ENDPOINT
from config import OPENSEARCH_PASSWORD
from config import OPENSEARCH_USERNAME
from config import REGION_NAME
from opensearchpy import OpenSearch
from opensearchpy import RequestsHttpConnection
from opensearchpy.helpers import bulk
from requests.auth import HTTPBasicAuth

from .base import BaseEmbedderService
from .base import BaseEmbeddingGenerator
from .base import BaseStorage
from .base import ChunkData
from .base import EmbedderInput
from .base import EmbedderOutput


class BedrockEmbeddingGenerator(BaseEmbeddingGenerator):
    """Bedrock implementation of embedding generator."""

    def __init__(self, region_name: str = REGION_NAME, max_workers: int = MAX_WORKERS):
        self.bedrock = boto3.client('bedrock-runtime', region_name=region_name)
        self.max_workers = max_workers
        self.embedding_cache: dict[str, List[float]] = {}

    def get_embedding_batch(self, texts: List[str]) -> Dict[int, List[float]]:
        """Generate embeddings for multiple texts using Bedrock."""
        embeddings = {}

        def get_single_embedding(text_item):
            text, idx = text_item

            if text in self.embedding_cache:
                return idx, self.embedding_cache[text]

            model_id = 'amazon.titan-embed-text-v2:0'
            body = {'inputText': text}

            try:
                response = self.bedrock.invoke_model(
                    modelId=model_id,
                    body=json.dumps(body),
                    contentType='application/json',
                    accept='application/json',
                )
                result = json.loads(response['body'].read())
                embedding = result['embedding']
                self.embedding_cache[text] = embedding
                return idx, embedding
            except Exception as e:
                logger.error(f'Lỗi tạo embedding cho text {idx}: {e}')
                return idx, None

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            text_items = [(text, idx) for idx, text in enumerate(texts)]
            future_to_text = {executor.submit(get_single_embedding, item): item for item in text_items}

            for future in as_completed(future_to_text):
                idx, embedding = future.result()
                embeddings[idx] = embedding

        return embeddings


class OpenSearchStorage(BaseStorage):
    """OpenSearch implementation of storage backend."""

    def __init__(
        self,
        endpoint: str = OPENSEARCH_ENDPOINT,
        username: str = OPENSEARCH_USERNAME,
        password: str = OPENSEARCH_PASSWORD,
        index_name: str = INDEX_NAME,
    ):
        self.index_name = index_name
        auth = HTTPBasicAuth(username, password)
        self.client = OpenSearch(
            hosts=[{'host': endpoint, 'port': 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=60,
            max_retries=3,
            retry_on_timeout=True,
        )

    def test_connection(self) -> bool:
        """Test connection to OpenSearch."""
        try:
            info = self.client.info()
            logger.info(f'Kết nối AWS OpenSearch thành công: {info}')
            return True
        except Exception as e:
            logger.error(f'Lỗi kết nối AWS OpenSearch: {e}')
            return False

    def create_optimized_index(self) -> None:
        """Create optimized index for OpenSearch."""
        if self.client.indices.exists(index=self.index_name):
            logger.info(f'Index {self.index_name} đã tồn tại.')
            return

        mapping = {
            'settings': {
                'index': {
                    'knn': True,
                    'knn.algo_param.ef_search': 512,
                    'number_of_shards': 3,
                    'number_of_replicas': 1,
                    'refresh_interval': '30s',
                    'max_result_window': 10000,
                    'blocks': {
                        'read_only_allow_delete': False,
                    },
                },
            },
            'mappings': {
                'properties': {
                    'id': {'type': 'keyword'},
                    'content': {
                        'type': 'text',
                        'analyzer': 'standard',
                        'search_analyzer': 'standard',
                    },
                    'embedding_vector': {
                        'type': 'knn_vector',
                        'dimension': 1024,
                        'method': {
                            'name': 'hnsw',
                            'space_type': 'cosinesimil',
                            'engine': 'nmslib',
                            'parameters': {
                                'ef_construction': 512,
                                'm': 16,
                            },
                        },
                    },
                    'filename': {'type': 'keyword'},
                    'position': {'type': 'integer'},
                    'tokens': {'type': 'integer'},
                    'section_title': {
                        'type': 'text',
                        'analyzer': 'standard',
                        'fields': {
                            'keyword': {'type': 'keyword'},
                        },
                    },
                    'type': {'type': 'keyword'},
                    'content_json': {'type': 'object', 'enabled': False},
                    'heading_level': {'type': 'integer'},
                },
            },
        }

        try:
            self.client.indices.create(index=self.index_name, body=mapping)
            logger.info(f'Tạo index {self.index_name} thành công.')
        except Exception as e:
            logger.error(f'Lỗi tạo index: {e}')
            raise

    def bulk_index_chunks(self, chunks: List[ChunkData], embeddings: Dict[int, List[float]]) -> None:
        """Bulk index chunks with embeddings."""
        actions = []
        successful_count = 0

        for idx, chunk in enumerate(chunks):
            embedding = embeddings.get(idx)
            if embedding is None:
                logger.warning(f'Bỏ qua chunk ID {chunk.id} vì lỗi embedding.')
                continue

            action = {
                '_index': self.index_name,
                '_id': chunk.id,
                '_source': {
                    'id': chunk.id,
                    'content': chunk.content,
                    'embedding_vector': embedding,
                    'filename': chunk.filename,
                    'position': chunk.position,
                    'tokens': chunk.tokens,
                    'section_title': chunk.section_title,
                    'type': chunk.type,
                    'content_json': chunk.content_json,
                    'heading_level': chunk.heading_level,
                },
            }
            actions.append(action)
            successful_count += 1

        logger.info(f'Đang bulk index {len(actions)} documents...')
        try:
            success, failed = bulk(
                self.client,
                actions,
                index=self.index_name,
                chunk_size=50,
                request_timeout=120,
                max_retries=5,
            )
            logger.info(f'Bulk index hoàn thành: {success} thành công, {len(failed)} thất bại')
            self.client.indices.refresh(index=self.index_name)
        except Exception as e:
            logger.error(f'Lỗi bulk index: {e}')
            raise


class EmbedderService(BaseEmbedderService):
    """Main embedder service that orchestrates the embedding process."""

    def __init__(
        self,
        embedding_generator: None,
        storage: None,
    ):
        self.embedding_generator = embedding_generator or BedrockEmbeddingGenerator()
        self.storage = storage or OpenSearchStorage()

    def process(self, input_data: EmbedderInput) -> EmbedderOutput:
        """Process a single embedding request."""
        try:
            # Generate embedding for single text
            embeddings = self.embedding_generator.get_embedding_batch([input_data.chunk])
            embedding = embeddings.get(0)

            return EmbedderOutput(
                id=input_data.metadata.get('id'),
                index_name=INDEX_NAME,
                embedding=embedding,
            )
        except Exception as e:
            logger.error(f'Lỗi xử lý embedding: {e}')
            return EmbedderOutput(
                id=input_data.metadata.get('id'),
                index_name=INDEX_NAME,
                embedding=None,
            )

    def process_chunks(self, chunks: List[ChunkData]) -> bool:
        """Process multiple chunks with embeddings and storage."""
        try:
            # Test connection first
            if not self.storage.test_connection():
                logger.error('Không thể kết nối với opensearch')
                return False

            # Create index if not exists
            self.storage.create_optimized_index()

            # Process embeddings
            start_time = time.time()
            texts = [chunk.content for chunk in chunks]
            logger.info(f'Đang tạo embedding cho {len(texts)} chunks...')

            embeddings = self.embedding_generator.get_embedding_batch(texts)

            # Store in backend
            self.storage.bulk_index_chunks(chunks, embeddings)

            end_time = time.time()
            logger.info(f'Thời gian xử lý: {end_time - start_time:.2f} giây')

            return True

        except Exception as e:
            logger.error(f'Lỗi xử lý chunks: {e}')
            return False

from __future__ import annotations

import asyncio
import json
import time
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from typing import Dict
from typing import List
from typing import Optional

import boto3
from opensearchpy import OpenSearch
from opensearchpy import RequestsHttpConnection
from opensearchpy.helpers import bulk
from requests.auth import HTTPBasicAuth  # type: ignore

from .base import BaseEmbedderService
from .base import BaseEmbeddingGenerator
from .base import BaseStorage
from .base import ChunkData
from .base import EmbedderInput
from .base import EmbedderOutput
from .config import INDEX_NAME
from .config import logger
from .config import MAX_WORKERS
from .config import OPENSEARCH_ENDPOINT
from .config import OPENSEARCH_PASSWORD
from .config import OPENSEARCH_USERNAME
from .config import REGION_NAME


class BedrockEmbeddingGenerator(BaseEmbeddingGenerator):
    """Bedrock implementation of embedding generator."""

    def __init__(self, region_name: str = REGION_NAME, max_workers: int = MAX_WORKERS):
        self.bedrock = boto3.client('bedrock-runtime', region_name=region_name)
        self.max_workers = max_workers
        self.embedding_cache: dict[str, List[float]] = {}
        self.semaphore = asyncio.Semaphore(max_workers)

    async def get_embedding_batch(self, texts: List[str]) -> Dict[int, List[float]]:
        """Generate embeddings for multiple texts using Bedrock."""

        async def get_single_embedding(text: str, idx: int) -> tuple[int, Optional[List[float]]]:
            async with self.semaphore:
                if text in self.embedding_cache:
                    return idx, self.embedding_cache[text]

                model_id = 'amazon.titan-embed-text-v2:0'
                body = {'inputText': text}

                try:
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(
                        None,
                        lambda: self.bedrock.invoke_model(
                            modelId=model_id,
                            body=json.dumps(body),
                            contentType='application/json',
                            accept='application/json',
                        ),
                    )

                    result = json.loads(response['body'].read())
                    embedding = result['embedding']
                    self.embedding_cache[text] = embedding
                    return idx, embedding

                except Exception as e:
                    logger.error(f'Lỗi tạo embedding cho text {idx}: {e}')
                    return idx, None

        tasks = [get_single_embedding(text, idx) for idx, text in enumerate(texts)]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        embeddings = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f'Task failed with exception: {result}')
                continue
            idx, embedding = result  # type: ignore
            embeddings[idx] = embedding

        return embeddings  # type: ignore


class OpenSearchStorage(BaseStorage):
    """OpenSearch implementation of storage backend."""

    def __init__(
        self,
        endpoint: Optional[str] = OPENSEARCH_ENDPOINT,
        username: str = OPENSEARCH_USERNAME,
        password: Optional[str] = OPENSEARCH_PASSWORD,
        index_name: str = INDEX_NAME,
    ):
        self.index_name = index_name

        if endpoint is None:
            raise ValueError('OPENSEARCH_ENDPOINT is required')
        if password is None:
            raise ValueError('OPENSEARCH_PASSWORD is required')

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
                    'number_of_shards': 1,
                    'number_of_replicas': 2,
                    'refresh_interval': '30s',
                    'max_result_window': 10000,
                    'blocks': {
                        'read_only_allow_delete': False,
                    },
                },
            },
            'mappings': {
                'properties': {
                    'id': {'type': 'integer'},
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

    def get_max_id(self) -> int:
        try:
            body = {
                'size': 0,
                'aggs': {
                    'max_id': {'max': {'field': 'id'}},
                },
            }
            res = self.client.search(index=self.index_name, body=body)
            max_id = res['aggregations']['max_id']['value']
            return int(max_id) if max_id is not None else 0
        except Exception as e:
            logger.error(f'Lỗi lấy max id: {e}')
            return 0

    def bulk_index_chunks(self, chunks: List[ChunkData], embeddings: Dict[int, List[float]]) -> None:
        actions = []
        successful_count = 0

        max_id = self.get_max_id()

        for idx, chunk in enumerate(chunks):
            embedding = embeddings.get(idx)
            if embedding is None:
                logger.warning('Bỏ qua chunk vì lỗi embedding.')
                continue

            chunk_id = max_id + idx + 1

            action = {
                '_index': self.index_name,
                '_id': chunk_id,
                '_source': {
                    'id': chunk_id,
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
                chunk_size=100,
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

    async def process(self, input_data: EmbedderInput) -> EmbedderOutput:
        """Process multiple chunks with embeddings and storage."""
        try:
            # Test connection first
            if not self.storage.test_connection():
                logger.error('Không thể kết nối với opensearch')
                return EmbedderOutput(
                    index_name=None,
                    num_embeddings=0,
                )

            # Create index if not exists
            self.storage.create_optimized_index()
            chunks = input_data.chunks
            # Process embeddings
            start_time = time.time()
            texts = [chunk.content for chunk in chunks]
            logger.info(f'Đang tạo embedding cho {len(texts)} chunks...')

            embeddings = await self.embedding_generator.get_embedding_batch(texts)

            # Store in backend
            self.storage.bulk_index_chunks(chunks, embeddings)

            end_time = time.time()
            logger.info(f'Thời gian xử lý: {end_time - start_time:.2f} giây')

            return EmbedderOutput(
                index_name=self.storage.index_name,
                num_embeddings=len(chunks),
            )

        except Exception as e:
            logger.error(f'Lỗi xử lý chunks: {e}')
            return EmbedderOutput(
                index_name=None,
                num_embeddings=0,
            )

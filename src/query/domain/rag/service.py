from __future__ import annotations

import os
from typing import Any
from typing import Dict
from typing import List

import boto3
from dotenv import load_dotenv
from infra.llm.bedrock import BedrockLLMClient
from infra.opensearch.retriever import OpenSearchRetriever
from langchain_aws.embeddings import BedrockEmbeddings
from shared.logging import get_logger
load_dotenv()

logger = get_logger(__name__)


class RAG:
    def __init__(self):
        # Environment variables with validation
        self.region = os.getenv('AWS_REGION', 'ap-southeast-2')
        self.index_name = os.getenv('OPENSEARCH_INDEX', 'semantic_chunks')
        self.bedrock_model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
        self.bedrock_embedding_model_id = os.getenv('BEDROCK_EMBEDDING_MODEL_ID', 'amazon.titan-embed-text-v2:0')
        self.opensearch_endpoint = os.getenv('OPENSEARCH_ENDPOINT')
        self.opensearch_username = os.getenv('OPENSEARCH_USERNAME')
        self.opensearch_password = os.getenv('OPENSEARCH_PASSWORD')
        self.tenant_id = os.getenv('TENANT_ID')

        # Validate required environment variables
        if not self.opensearch_endpoint:
            raise ValueError('OPENSEARCH_ENDPOINT environment variable is required')
        if not self.opensearch_password:
            raise ValueError('OPENSEARCH_PASSWORD environment variable is required')

        try:
            self.llm_client = BedrockLLMClient(self.region, self.bedrock_model_id)
            bedrock_client = boto3.client('bedrock-runtime', region_name=self.region)
            self.embeddings_client = BedrockEmbeddings(client=bedrock_client, model_id=self.bedrock_embedding_model_id)
            # logger.info("RAG components initialized successfully")
            # test = self.embeddings_client.embed_query("test")
            # print(f"Embedding test successful: {test[:5]}...")  # Print first 5 elements of the embedding for verification
            self.retriever = OpenSearchRetriever(
                index_name=self.index_name,
                opensearch_username=self.opensearch_username,
                opensearch_password=self.opensearch_password,
                bedrock_embeddings_client=self.embeddings_client,
                opensearch_endpoint=self.opensearch_endpoint,
            )
        except Exception as e:
            logger.error(f'Failed to initialize RAG components: {str(e)}')
            raise

    def process(self, question: str) -> Dict[str, Any]:
        try:
            # Build search kwargs
            search_kwargs = {}
            if self.tenant_id:
                search_kwargs['filter'] = {'term': {'tenant_id': self.tenant_id}}

            # Retrieve relevant documents
            docs = self.retriever.get_relevant_documents(question, k=4, search_kwargs=search_kwargs)

            # Extract context and sources
            context = ''
            sources = []
            if docs:
                context = '\n'.join([doc.page_content for doc in docs])
                sources = [getattr(doc, 'metadata', {}).get('source', 'Unknown') for doc in docs]

            # Generate prompt
            prompt = self._build_prompt(context, question)

            # Generate answer
            answer = self.llm_client.generate(prompt=prompt, context='')

            return {
                'answer': answer,
                'sources': sources,
            }

        except Exception as e:
            logger.error(f'Error processing RAG request: {str(e)}')
            raise

    def _build_prompt(self, context: str, question: str) -> str:
        return f"""
Context:
{context}

Question: {question}

Answer:"""

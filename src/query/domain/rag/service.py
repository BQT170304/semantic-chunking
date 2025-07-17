from __future__ import annotations

import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

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

    def process(self, question: str, chat_history: Any = None, documents: Optional[List[str]] = None) -> Dict[str, Any]:
        try:
            # Build search kwargs
            search_kwargs = {}

            # Build filters for tenant_id and documents
            filters = []

            # Add tenant_id filter if available
            if self.tenant_id:
                filters.append({'term': {'tenant_id': self.tenant_id}})

            # Add document filename filter if documents are specified
            if documents:
                # Use terms query for multiple filenames
                filters.append({'terms': {'filename': documents}})

            if filters:
                if len(filters) == 1:
                    search_kwargs['filter'] = filters[0]
                else:
                    search_kwargs['filter'] = {
                        'bool': {
                            'must': filters,
                        },
                    }

            # Retrieve relevant documents
            docs = self.retriever.get_relevant_documents(question, k=3, search_kwargs=search_kwargs)

            # Extract context and sources
            context = ''
            sources = []
            if docs:
                context = '\n'.join([doc.page_content for doc in docs])
                # source = "{filename: filename, section_title: section_title, content: content}"
                sources = [
                    {
                        'filename': doc.metadata.get('filename', 'unknown'),
                        'section_title': doc.metadata.get('section_title', 'unknown'),
                        'content': doc.page_content,
                    }
                    for doc in docs
                ]

            # Generate prompt
            system_prompt = "You are a helpful assistant. Use the provided context and chat history to answer the user's question as accurately as possible."
            chat_history_str = self._format_chat_history(chat_history)
            prompt = self._build_prompt(system_prompt, chat_history_str, context, question)

            # Generate answer
            answer = self.llm_client.generate(prompt=prompt, context='')

            return {
                'message': answer,
                'sources': sources,
            }

        except Exception as e:
            logger.error(f'Error processing RAG request: {str(e)}')
            raise

    def _format_chat_history(self, chat_history: Any) -> str:
        if not chat_history:
            return ''
        # Expecting a list of dicts with 'role' and 'content'
        formatted = []
        for turn in chat_history:
            role = turn.get('role', 'user')
            content = turn.get('content', '')
            formatted.append(f'{role.capitalize()}: {content}')
        return '\n'.join(formatted)

    def _build_prompt(self, system_prompt: str, chat_history: str, context: str, question: str) -> str:
        return f"""
{system_prompt}

Chat History:
{chat_history}

Context:
{context}

Question: {question}

Answer:"""

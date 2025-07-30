from __future__ import annotations

import json
import os

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from shared.logging.logger import get_logger

from .prompt_builder import build_markdown_prompt

# Initialize logger
logger = get_logger(__name__)
load_dotenv()


class NovaMarkdownGenerator:
    def __init__(self, region_name=None, model_id=None):
        # Use region_name parameter or fall back to environment variable
        if region_name:
            self.region_name = region_name
        else:
            self.region_name = os.getenv('AWS_BEDROCK_REGION', 'ap-southeast-2')  # Default to ap-southeast-2 if not set
        self.client = boto3.client('bedrock-runtime', region_name=self.region_name)

        # Allow model override via parameter or environment variable
        if model_id:
            self.model_id = model_id
        elif os.getenv('AWS_BEDROCK_MODEL_ID'):
            self.model_id = os.getenv('AWS_BEDROCK_MODEL_ID')
        else:
            self.model_id = 'amazon.nova-micro-v1:0'  # Default Nova Micro model ID

        logger.info(
            'Initialized NovaMarkdownGenerator',
            region=self.region_name,
            model_id=self.model_id,
        )

    async def generate(self, raw_text: str) -> str:
        prompt = build_markdown_prompt(raw_text)
        logger.info('Generating markdown', model_id=self.model_id, input_length=len(raw_text))

        body = {
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {
                            'text': prompt,
                        },
                    ],
                },
            ],
            'inferenceConfig': {
                'max_new_tokens': 8192,
                'temperature': 0.4,
            },
        }

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json',
            )

            # Read response according to Bedrock API format
            response_body = response['body'].read()
            response_data = json.loads(response_body)

            # Nova models return output in a different format
            result = response_data['output']['message']['content'][0]['text']
            logger.info(
                'Markdown generation completed',
                model_id=self.model_id,
                output_length=len(result),
                status='success',
            )

            return result

        except ClientError as e:
            if 'AccessDeniedException' in str(e):
                logger.error(
                    'Access denied to model',
                    model_id=self.model_id,
                    error='AccessDenied',
                    suggestion='Request access to Nova models in AWS Bedrock console',
                )
                raise Exception(f'No access to model {self.model_id}. Check AWS Bedrock permissions.')
            else:
                logger.error(
                    'Unexpected error during generation',
                    model_id=self.model_id,
                    error=str(e),
                    status='failed',
                )
                raise

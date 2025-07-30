from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
REGION_NAME = os.getenv('REGION_NAME', 'ap-southeast-2')
MAX_WORKERS = 16
OPENSEARCH_ENDPOINT = os.getenv('OPENSEARCH_ENDPOINT')
OPENSEARCH_USERNAME = os.getenv('OPENSEARCH_USERNAME', 'op')
OPENSEARCH_PASSWORD = os.getenv('OPENSEARCH_PASSWORD')
INDEX_NAME = os.getenv('INDEX_NAME', 'semantic_chunks')

from __future__ import annotations

import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
REGION_NAME = 'ap-southeast-2'
MAX_WORKERS = 10
OPENSEARCH_ENDPOINT = 'search-semantic-chunking-po2nyenkrwlaepdg4yjmpunhly.aos.ap-southeast-2.on.aws'
OPENSEARCH_USERNAME = 'op'
OPENSEARCH_PASSWORD = '6bcq#NhYf6G0KV'
INDEX_NAME = 'semantic_chunks'

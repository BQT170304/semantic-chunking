# Semantic Chunking for Multi-format Documents

A RAG (Retrieval-Augmented Generation) application that allows uploading and querying information from document files with intelligent semantic chunking capabilities.

## Features

- **Document Upload**: Support for multiple file formats (PDF, Word, Text, etc.)
- **Semantic Chunking**: Automatically split documents into meaningful segments
- **RAG Query**: Query information from uploaded documents using natural language
- **Real-time Chat**: User-friendly chat interface to interact with documents
- **Document Management**: Manage list of uploaded documents
- **Vector Search**: High-accuracy semantic search

## Architecture

- **Backend**: FastAPI with 2 microservices:
  - Upload Service (Port 8000): Handle document upload and chunking
  - Query Service (Port 8001): Handle RAG queries
- **Frontend**: Next.js with TailwindCSS
- **Vector Database**: OpenSearch/Elasticsearch
- **LLM**: AWS Bedrock or other LLM providers

## Setup and Installation

## Setup and Installation

### 1. Create Environment File

Create a `.env` file in the root directory with the following configuration:

```env
# Database Configuration
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_USERNAME=admin
OPENSEARCH_PASSWORD=admin
OPENSEARCH_INDEX=documents

# LLM Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# API Configuration
UPLOAD_SERVICE_URL=http://localhost:8000
QUERY_SERVICE_URL=http://localhost:8001
FRONTEND_URL=http://localhost:3000

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000

# File Storage
MAX_FILE_SIZE=50MB
ALLOWED_FILE_TYPES=pdf,docx,txt,md
```

### 2. Run Backend with Docker

```bash
# Build and run all services
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

Backend services will run on:

- Upload Service: http://localhost:8000
- Query Service: http://localhost:8001

### 3. Run Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Or build and run production
npm run build
npm run start
```

Frontend will run on: http://localhost:3000

## How to Use

1. **Upload Documents**:

   - Access the web interface
   - Drag and drop or select files to upload
   - Wait for the system to process and chunk the document

2. **Query Information**:

   - Use the chat interface
   - Ask questions about document content
   - Receive answers with reference information

3. **Manage Documents**:
   - View list of uploaded documents
   - Delete unnecessary documents

## Development Setup

### Set up

1. Pre-commit formating code:

   - Install:

   ```bash
   pip install pre-commit
   ```

   - Add pre-commit to git hook:

   ```bash
   pre-commit install
   ```

   - Run pre-commit for formating code (only staged files in git):

   ```bash
   pre-commit run
   ```

   - Run pre-commit for formating code with all files:

   ```bash
   pre-commit run --all-files
   ```

## API Documentation

### Upload Service (Port 8000)

- `POST /api/upload`: Upload and process documents
- `GET /api/documents`: Get list of documents
- `DELETE /api/documents/{id}`: Delete document

### Query Service (Port 8001)

- `POST /api/query`: Query information from documents
- `GET /api/health`: Check service status

Access Swagger UI:

- Upload Service: http://localhost:8000/docs
- Query Service: http://localhost:8001/docs

## Troubleshooting

### Common Issues:

1. **Docker containers not starting**:

   ```bash
   # Check logs
   docker-compose logs

   # Rebuild containers
   docker-compose down
   docker-compose up -d --build
   ```

2. **Frontend cannot connect to backend**:

   - Check if `.env` file has correct URLs
   - Ensure backend is running on correct ports

3. **File upload fails**:

   - Check if file format is supported
   - Check if file size exceeds limit

4. **LLM not working**:
   - Check AWS credentials in `.env` file
   - Ensure AWS Bedrock access permissions

## Acknowledgments

- AWS services
- FastAPI for backend framework
- Next.js for frontend framework

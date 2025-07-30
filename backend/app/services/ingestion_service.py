import os
import logging
from typing import Dict, Any, List
from pathlib import Path
from pdfminer.high_level import extract_text
import docx
import pytesseract
from PIL import Image
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..db.milvus_client import MilvusDBClient
from ..adapters.openai_adapter import OpenAIAdapter
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading        
from ..adapters.openai_adapter import OpenAIAdapter
from ..core.config import settings
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles extraction of text from various document types"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            return extract_text(file_path)
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            return ""

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            return " ".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {file_path}: {e}")
            return ""

    @staticmethod
    def extract_text_from_image(file_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(file_path)
            return pytesseract.image_to_string(image)
        except Exception as e:
            logger.error(f"Error extracting text from image {file_path}: {e}")
            return ""

    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error extracting text from TXT {file_path}: {e}")
            return ""

class IngestionService:
    """Service for ingesting documents into the vector database"""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.milvus_client = MilvusDBClient()
        
        # Initialize embedding client with proper API key
        try:
            from ..core.secrets import get_secret
            api_key = get_secret("OPENAI_API_KEY", "development")
        except ImportError:
            # Fallback to environment variable
            import os
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set in the environment or .env file.")
        
        self.embedding_client = OpenAIAdapter(api_key=api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def get_database_status(self) -> Dict[str, Any]:
        """Get the status of the vector database"""
        try:
            # Check if Milvus is available
            self.milvus_client._ensure_connected()
            return {
                "type": "milvus",
                "status": "active",
                "fallback": False
            }
        except Exception as e:
            logger.error(f"Milvus connection failed: {e}")
            return {
                "type": "milvus",
                "status": "error",
                "error": str(e),
                "fallback": False
            }

    async def ingest_document(self, file_path: str) -> Dict[str, Any]:
        """Ingest a document into the vector database"""
        try:
            # Extract text from document
            file_path = Path(file_path)
            if not file_path.exists():
                return {"success": False, "error": f"File not found: {file_path}"}

            # Extract text based on file type
            file_extension = file_path.suffix.lower()
            if file_extension == '.pdf':
                text = self.document_processor.extract_text_from_pdf(str(file_path))
            elif file_extension == '.docx':
                text = self.document_processor.extract_text_from_docx(str(file_path))
            elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                text = self.document_processor.extract_text_from_image(str(file_path))
            elif file_extension == '.txt':
                text = self.document_processor.extract_text_from_txt(str(file_path))
            else:
                return {"success": False, "error": f"Unsupported file type: {file_extension}"}

            if not text.strip():
                return {"success": False, "error": "No text extracted from document"}

            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            if not chunks:
                return {"success": False, "error": "No text chunks generated"}

            # Prepare documents for insertion
            documents = []
            embeddings = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                doc = {
                    "content": chunk,
                    "source": str(file_path),
                    "filename": file_path.name,
                    "file_type": file_extension,
                    "chunk_id": f"{file_path.stem}_{i}",
                    "timestamp": time.time()
                }
                documents.append(doc)
                ids.append(f"{file_path.stem}_{i}")

            # Generate embeddings for chunks
            embeddings = []
            for chunk in chunks:
                try:
                    embedding = await self.embedding_client.create_embedding(chunk)
                    embeddings.append(embedding)
                except Exception as e:
                    logger.error(f"Error generating embedding: {e}")
                    return {"success": False, "error": f"Embedding generation failed: {e}"}

            # Insert into Milvus
            success = self.milvus_client.insert_documents(documents, embeddings, ids)
            
            if success:
                return {
                    "success": True,
                    "filename": file_path.name,
                    "chunks_processed": len(chunks),
                    "database_type": "milvus"
                }
            else:
                return {"success": False, "error": "Failed to insert documents into Milvus"}

        except Exception as e:
            logger.error(f"Error ingesting document: {e}")
            return {"success": False, "error": str(e)}

    def search_documents(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Search for documents similar to the query"""
        try:
            # Generate embedding for query
            import asyncio
            query_embedding = asyncio.run(self.embedding_client.create_embedding(query))
            
            # Search in Milvus
            results = self.milvus_client.search_similar(query_embedding, limit)
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "database_type": "milvus"
            }
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return {"success": False, "error": str(e)}
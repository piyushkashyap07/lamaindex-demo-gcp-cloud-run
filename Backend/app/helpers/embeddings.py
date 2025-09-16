import pandas as pd
import numpy as np
from typing import List, Dict, Any
import os
from pinecone import Pinecone, ServerlessSpec
from llama_index.embeddings.openai import OpenAIEmbedding
import logging
from tqdm import tqdm
from openai import OpenAI
import re

logger = logging.getLogger(__name__)

class EmbeddingsProcessor:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        
    def _sanitize_index_name(self, index_name: str) -> str:
        """Sanitize index name to follow Pinecone naming requirements"""
        # Replace underscores and spaces with hyphens
        sanitized = re.sub(r'[_\s]+', '-', index_name.lower())
        # Remove any other special characters
        sanitized = re.sub(r'[^a-z0-9-]', '', sanitized)
        # Ensure it starts with a letter
        if not sanitized[0].isalpha():
            sanitized = f"idx-{sanitized}"
        return sanitized
        
    def _create_pinecone_index(self, index_name: str, dimension: int = 1536):
        """Create a Pinecone index if it doesn't exist"""
        try:
            # Sanitize index name
            sanitized_name = self._sanitize_index_name(index_name)
            logger.info(f"Using index name: {sanitized_name}")
            
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            if sanitized_name not in existing_indexes:
                # Create new index with us-east-1 region for free plan
                self.pc.create_index(
                    name=sanitized_name,
                    dimension=dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"  # Changed to us-east-1 for free plan
                    )
                )
                logger.info(f"Created new Pinecone index: {sanitized_name}")
            return self.pc.Index(sanitized_name)
        except Exception as e:
            logger.error(f"Error creating Pinecone index: {e}")
            raise

    def _process_excel_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Process Excel file and return list of documents with metadata"""
        try:
            df = pd.read_excel(file_path)
            documents = []
            
            # Combine 'text' and 'categories' columns if they exist
            for _, row in df.iterrows():
                text = row.get('text', '')
                categories = row.get('categories', '')
                
                # Create document with metadata
                doc = {
                    'content': text,
                    'metadata': {
                        'categories': categories,
                        'source': os.path.basename(file_path)
                    }
                }
                documents.append(doc)
                
            return documents
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}")
            raise

    def _create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts using OpenAI's API"""
        try:
            embeddings = []
            for text in tqdm(texts, desc="Creating embeddings"):
                response = self.openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text
                )
                embedding = response.data[0].embedding
                embeddings.append(embedding)
            return embeddings
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise

    def _prepare_vectors(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]) -> List[Dict[str, Any]]:
        """Prepare vectors for Pinecone upload"""
        vectors = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            # Create a unique ID for each document
            doc_id = f"doc_{i}"
            
            # Add the vector
            vectors.append({
                "id": doc_id,
                "values": embedding,
                "metadata": doc['metadata']
            })
        return vectors

    def load_and_upload_data(self, excel_file_path: str, index_name: str = "company-analysis-docs"):
        """Main function to process Excel data and upload to Pinecone"""
        try:
            # Process Excel data
            logger.info(f"Processing Excel file: {excel_file_path}")
            documents = self._process_excel_data(excel_file_path)
            
            # Extract text content for embeddings
            texts = [doc['content'] for doc in documents]
            
            # Create embeddings
            logger.info("Creating embeddings...")
            embeddings = self._create_embeddings(texts)
            
            # Prepare vectors for Pinecone
            vectors = self._prepare_vectors(documents, embeddings)
            
            # Create/Get Pinecone index
            index = self._create_pinecone_index(index_name)
            
            # Upload vectors to Pinecone
            logger.info(f"Uploading {len(vectors)} vectors to Pinecone...")
            index.upsert(vectors=vectors)
            
            logger.info("Data upload completed successfully")
            return {
                "status": "success",
                "documents_processed": len(documents),
                "vectors_uploaded": len(vectors)
            }
            
        except Exception as e:
            logger.error(f"Error in load_and_upload_data: {e}")
            raise

# Example usage
if __name__ == "__main__":
    processor = EmbeddingsProcessor()
    result = processor.load_and_upload_data("path_to_your_excel_file.xlsx")
    print(result) 
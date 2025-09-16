import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Union, Tuple
import logging
# from pinecone import Pinecone # Pinecone is not used for direct index operations here
from langchain_openai import OpenAIEmbeddings
# from sentence_transformers import CrossEncoder

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Environment keys
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY") # Still here, but not used in this snippet
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws") # Still here, but not used in this snippet
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1") # Still here, but not used in this snippet
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME") # Still here, but not used in this snippet
CROSS_ENCODER_MODEL = os.getenv("CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


from pymongo import MongoClient

def get_mongo_db():
    client = MongoClient( os.getenv("MONGODB_RAG_URI"), tlsAllowInvalidCertificates=True)
    db = client[os.getenv('MONGODB_RAG_DB')]
    collection = db['company-analysis-data']
    return collection


def generate_embeddings(text: str) -> List[float]:
    """
    Generate embeddings for the input text using OpenAI embeddings.

    Args:
        text: The text to generate embeddings for

    Returns:
        List of embedding values
    """
    try:
        # Initialize embeddings model each time
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=OPENAI_API_KEY
        )

        text = text.replace("\n", " ")  # Remove newline characters for clean input
        return embeddings.embed_query(text)
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        return []

def pair_query_with_docs(query: str, retrieved_docs: List[str]) -> List[List[str]]:
    """
    Creates pairs of query and each retrieved document for cross-encoder scoring.

    Args:
        query: The search query
        retrieved_docs: List of retrieved document texts

    Returns:
        List of query-document pairs
    """
    return [[query, doc] for doc in retrieved_docs]

# def rerank_documents(query: str, retrieved_docs: List[str], top_k: int = 3) -> List[str]:
#     """
#     Uses a cross-encoder to score and rerank retrieved documents.

#     Args:
#         query: The search query
#         retrieved_docs: List of retrieved document texts
#         top_k: Number of top documents to return

#     Returns:
#         List of reranked document texts
#     """
#     try:
#         # Initialize cross-encoder each time
#         cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)

#         # Create query-document pairs
#         pairs = pair_query_with_docs(query, retrieved_docs)

#         # Get scores from cross-encoder
#         scores = cross_encoder.predict(pairs)

#         # Zip scores with documents
#         scored_docs = list(zip(scores, retrieved_docs))

#         # Sort documents by score in descending order
#         reranked_docs = sorted(scored_docs, key=lambda x: x[0], reverse=True)

#         # Return top-k ranked documents
#         return [doc for _, doc in reranked_docs[:top_k]]
#     except Exception as e:
#         logger.error(f"Error reranking documents: {e}")
#         return retrieved_docs[:top_k] if retrieved_docs and len(retrieved_docs) > top_k else retrieved_docs

# --- MODIFIED get_document_context function ---
async def get_document_context(query: str,company_identifier:str = "", top_k: int = 5) -> Union[str, List[Dict[str, Any]]]:
    """
    Retrieve document context from the Pinecone index and return as a formatted string or structured list.

    Args:
        query: The search query
        company_identifier: The category to filter documents by (based on your usage)
        top_k: Number of documents to retrieve

    Returns:
        A string containing error messages, or a list of dictionaries
        where each dictionary represents a retrieved document and includes
        'chunk', 'image_tags' (optional), and 'image_url' (optional).
    """
    try:
        query_embedding = generate_embeddings(query)

        if not query_embedding:
            logger.error("Failed to generate embeddings for query")
            return "No relevant information found: failed to generate query embeddings."

        try:
            collection = get_mongo_db()
            if company_identifier != "":
                results = collection.aggregate([
                    {
                        '$vectorSearch': {
                            "index": "default",
                            "path": "plot_embeddings",
                            "queryVector": query_embedding,
                            "numCandidates": 200,
                            "limit": top_k,
                        }
                    },
                    {
                        '$match': {
                            "ticker_id": {"$eq": company_identifier}
                        }
                    },
                ])
            else:
                results = collection.aggregate([
                    {
                        '$vectorSearch': {
                            "index": "default",
                            "path": "plot_embeddings",
                            "queryVector": query_embedding,
                            "numCandidates": 200,
                            "limit": top_k,
                        }
                    }
                ])

            retrieved_documents_data = []
            for doc in results:
                doc_data = {
                    "chunk": doc.get("chunk", "") # Ensure 'chunk' is always present
                }
                # Add image_tags and image_url if they exist and are not empty
                if "image_tags" in doc and doc["image_tags"]:
                    doc_data["image_tags"] = doc["image_tags"]
                if "image_url" in doc and doc["image_url"]:
                    doc_data["image_url"] = doc["image_url"]
                
                retrieved_documents_data.append(doc_data)

            if not retrieved_documents_data:
                logger.info("No relevant documents found for the query.")
                return "No relevant information found." # Return a descriptive string if no docs found

            return retrieved_documents_data # Return the list of dictionaries

        except Exception as e:
            error_msg = f"Error querying MongoDB collection: {e}"
            logger.error(error_msg)
            return f"Error retrieving documents from database: {error_msg}"

    except Exception as e:
        error_msg = f"Error retrieving document context: {e}"
        logger.error(error_msg)
        return f"Error retrieving information from knowledge base: {error_msg}"

def format_context_for_llm(docs: List[Dict[str, Any]]) -> str:
    """
    Format retrieved documents into a context string for the LLM.
    (This function might become less relevant if your LLM directly processes the JSON from semantic_report_search_tool)
    """
    if not docs:
        return "No relevant information found."

    formatted_docs = []
    for i, doc in enumerate(docs, 1):
        doc_entry = f"Document {i}:"
        doc_entry += f"\nContent: {doc.get('chunk', 'N/A')}"
        if "image_tags" in doc and doc["image_tags"]:
            doc_entry += f"\nImage Tags: {', '.join(doc['image_tags'])}"
        if "image_url" in doc and doc["image_url"]:
            doc_entry += f"\nImage URL: {doc['image_url']}"
        
        formatted_docs.append(doc_entry)

    return "\n\n" + "\n\n---\n\n".join(formatted_docs)

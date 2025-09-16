from pymongo import MongoClient
import os
import logging
from typing import Optional
from dotenv import load_dotenv
from bson.objectid import ObjectId

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class MongoDB:
    _instance = None
    _client: Optional[MongoClient] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._client:
            mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
            self._client = MongoClient(mongodb_uri, tlsAllowInvalidCertificates=True)
            self.db = self._client.get_database("propensity_score_db")
            logger.info("MongoDB connection initialized")
    
    def get_collection(self, collection_name: str):
        """Get a MongoDB collection"""
        return self.db[collection_name]
    
    def close(self):
        """Close the MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            logger.info("MongoDB connection closed")

# Create a singleton instance
mongodb = MongoDB() 


def get_user_conversation_history(conversation_id: str):
    """
    Connects to MongoDB, retrieves the last 12 messages for a given conversation ID,
    filters for 'user' roles, and returns them as a list of dictionaries.
    """
    # Replace with your MongoDB connection details
    collection = mongodb.get_collection('conversations')
    try:
        # MongoDB aggregation pipeline
        pipeline = [
            {
                "$match": {
                    "_id": ObjectId(conversation_id)
                }
            },
            {
                "$project": {
                    "messages": {
                        "$slice": ["$messages", -12] # Get the last 12 messages
                    }
                }
            },
            {
                "$unwind": "$messages" # Deconstruct the messages array
            },
            {
                "$match": {
                    "messages.role": "user" # Filter by role "user"
                }
            },
            {
                "$group": {
                    "_id": "$_id",
                    "user_messages": {
                        "$push": "$messages" # Reconstruct the array with only user messages
                    }
                }
            },
            {
                "$project": {
                    "_id": 0, # Exclude the _id field from the final output if not needed
                    "user_messages": 1
                }
            }
        ]

        result = list(collection.aggregate(pipeline))

        if result and 'user_messages' in result[0]:
            history_messages = [msg['content'] for msg in result[0]['user_messages']]
            print("Formatted user history: ",history_messages)
            return history_messages
        else:
            return [] # No messages found or no user messages in the last 12

    except Exception as e:
        print(f"An error occurred: {e}")
        return []
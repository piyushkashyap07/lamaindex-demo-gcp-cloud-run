from app.models.schema import ApiResponse
from app.helpers.mongodb import mongodb
from datetime import datetime
from app.models.schema import ConversationResponse
import json

async def create_conversation_handler(email):
    try:
        collection = mongodb.get_collection("conversations")
        conversation_data = {
            "email": email,
            "created_at": datetime.utcnow(),
            "status": "active",
            "messages": []
        }
        result = collection.insert_one(conversation_data)
        conversation_id = str(result.inserted_id)
        return ConversationResponse(
            conversation_id=conversation_id,
            email=email,
            created_at=conversation_data["created_at"],
            status=conversation_data["status"]
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        return ApiResponse(
            status_code=500,
            message=f"An error occurred: {str(e)}",
            data={}
        )

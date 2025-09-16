from app.models.schema import ApiResponse
from app.helpers.mongodb import mongodb

async def get_conversations():
    try: 
        # Get the conversations collection
        collection = mongodb.get_collection("conversations")
        
        # Fetch all documents and convert ObjectId to string for JSON serialization
        cursor = collection.find()
        data = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
            data.append(doc)
        
        return ApiResponse(
            status_code=200,
            message="Success",
            data={"conversations": data}
        )

    except Exception as e:
        print(f"An error occurred: {e}")
        return ApiResponse(
            status_code=500,
            message=f"An error occurred: {str(e)}",
            data={}
        )

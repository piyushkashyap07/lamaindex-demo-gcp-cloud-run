from pymongo import ReturnDocument
from app.models.schema import ApiResponse
from app.workflows.NewStock_workflow import run_new_stock_workflow
from app.helpers.mongodb import mongodb
from typing import Dict, Optional, Any, List
from bson import ObjectId
from fastapi.responses import StreamingResponse
from datetime import datetime

async def handle_messages(message, conversationID):
    try:
        collection = mongodb.get_collection('conversations')
        conversation = collection.find_one({"_id": ObjectId(conversationID)})
        if not conversation:
            raise ValueError(f"Conversation with ID {conversationID} not found")
        messages = conversation.get("messages", [])
        last_messages = messages[-6:] if len(messages) > 0 else []
        timestamp = datetime.utcnow()
        result =  collection.find_one_and_update(
            {"_id": ObjectId(conversationID)},
            {"$push": {"messages": {
                "role": "user",
                "content": message,
                "timestamp": timestamp
            }}},
            return_document=ReturnDocument.AFTER
        )
        message_Id =  len(result.get("messages", [])) + 1
        print(message_Id)
        handler = await run_new_stock_workflow(message, conversationID, message_Id)
        payload = {
            "conversation_id": conversationID,
            "user_message": message,
            "conversation_history": last_messages
        }

        async def event_generator():
            response_chunks = ""
            final_response_with_metadata = ""  # Initialize variable
            
            # Get the final result from the workflow
            try:
                final_result = await handler
                print(f"Final workflow result: {final_result}")
                
                # Extract the actual response from the workflow result
                if hasattr(final_result, 'result') and final_result.result:
                    workflow_response = final_result.result.get("response", "")
                    user_query = final_result.result.get("user_query", "")
                    propensity_score = final_result.result.get("propensity_score", 0.0)
                    score_category = final_result.result.get("score_category", "Unknown")
                else:
                    workflow_response = str(final_result) if final_result else "No response available"
                    user_query = message
                    propensity_score = 0.0
                    score_category = "Unknown"
                
                # Use the workflow response instead of the streaming chunks
                final_response = workflow_response if workflow_response else response_chunks
                
                # Create clean response object
                clean_response = {
                    "response": final_response,
                    "user_query": user_query,
                    "propensity_score": propensity_score,
                    "score_category": score_category
                }
                
                # Send clean response as stream
                yield f"data: {clean_response}\n\n"
                
                # Store the clean response for database
                final_response_with_metadata = final_response
                
            except Exception as e:
                print(f"Error processing workflow result: {e}")
                final_response_with_metadata = f"## Propensity Score Analysis: {message}\n\n**Error:** Unable to complete analysis. Please try again.\n\n*Technical details: {str(e)}*"
                response_metadata = {
                    "propensity_score": 0.0,
                    "score_category": "Error",
                    "analysis_type": "propensity_score",
                    "timestamp": datetime.utcnow().isoformat()
                }
                # Send error response as stream
                yield f"data: {final_response_with_metadata}\n\n"
                yield f"data: *Analysis completed with score: 0.0/100 (Error)*\n\n"
                yield "data: [DONE]\n\n"
            
            # Store the assistant response in the conversation history
            if final_response_with_metadata and "Answer to user_query :" in final_response_with_metadata:
                final_response_with_metadata = final_response_with_metadata.replace("Answer to user_query :", "").strip()

            if final_response_with_metadata:
                existing_msg = collection.find_one(
                    {"_id": ObjectId(conversationID), "messages.message_id": message_Id}
                )

                if existing_msg:
                    # Append to existing message (your original code)
                    collection.update_one(
                        {"_id": ObjectId(conversationID), "messages.message_id": message_Id},
                        [{"$set": {
                            "messages": {
                                "$map": {
                                    "input": "$messages", 
                                    "as": "msg",
                                    "in": {
                                        "$cond": {
                                            "if": {"$eq": ["$$msg.message_id", message_Id]},
                                            "then": {
                                                "$mergeObjects": [
                                                    "$$msg",
                                                    {"content": {"$concat": [final_response_with_metadata,"$$msg.content"]}}
                                                ]
                                            },
                                            "else": "$$msg"
                                        }
                                    }
                                }
                            }
                        }}]
                    )
                else:
                    collection.update_one(
                        {"_id": ObjectId(conversationID)},
                        {"$push": {"messages": {
                            "message_id": message_Id,
                            "role": "assistant",
                            "content": final_response_with_metadata,
                            "timestamp": datetime.utcnow()
                        }}}
                    )

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        print(f"An error occurred: {e}")
        return ApiResponse(
            status_code=500,
            message=f"An error occurred: {str(e)}",
            data={"response":"No response available"}
        )
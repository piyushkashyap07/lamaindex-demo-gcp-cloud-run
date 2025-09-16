import logging
from typing import Dict, Any, List
import asyncio
from llama_index.llms.openai import OpenAI

logger = logging.getLogger(__name__)

def filter_human_messages(conversation_history: List[Dict[str, Any]]) -> List[str]:
    """
    Filter the conversation history to get only user/human message content and limit to the last 6.
    
    Args:
        conversation_history: A list of conversation messages with 'role' and 'content' keys
        
    Returns:
        A list containing only the content of user messages, limited to the last 6
    """
    try:
        # Filter for messages with role 'user' and extract only the content
        human_message_contents = [msg.get('content', '') for msg in conversation_history if msg.get('role') == 'user']
        
        # Limit to the last 6 messages
        last_six_contents = human_message_contents[-6:] if len(human_message_contents) > 6 else human_message_contents
        
        logger.debug(f"Filtered human message contents (last 6): {last_six_contents}")
        # print("last_six_messages: ", last_six_contents)
        return last_six_contents
    
    except Exception as e:
        logger.error(f"Error filtering human messages: {e}")
        # Return empty list in case of error
        return []
    

async def condense_human_messages_to_query(messages: List[str], llm: Any) -> str:
    """
    Condense multiple human message contents into a single query using an LLM.
    
    Args:
        messages: A list of human/user message contents (strings)
        llm: The language model to use for condensing
        
    Returns:
        A condensed query string
    """
    if not messages:
        return ""
    
    try:
        # Get the latest message
        latest_message = messages[-1]
        
        # Combine previous messages if they exist
        previous_conversation = ""
        if len(messages) > 1:
            previous_messages = messages[:-1]
            for i, content in enumerate(previous_messages):
                previous_conversation += f"Message {i+1}: {content}\n"
        
        # Create a prompt for the LLM to condense the conversation
        # prompt = f"""
        # I need you to create a single, concise search query based on a conversation history.
        
        # LATEST USER QUERY:
        # {latest_message}
        
        # {"PREVIOUS CONVERSATION CONTEXT:" if previous_conversation else ""}
        # {previous_conversation}
        
        # Please create a search query that:
        # 1. Primarily focuses on answering the LATEST USER QUERY
        # 2. Incorporates relevant context from previous messages only if it helps clarify the latest query
        # 3. Is formulated as a clear, searchable query for a vector database
        # 4. Ignores any previous questions that are not directly related to the latest query
        
        # Condensed search query:
        # """

        prompt = f"""
            Given the user's chat history and latest question, generate a concise, search-friendly query in English. The primary goal is to preserve the original question whenever possible. Only summarize or modify if absolutely necessary for context or clarity. Follow these guidelines:

            Default approach: Use the latest question as is, without any modifications.

            Only if the latest question clearly requires context from the previous conversation to be understood:
            a. Briefly incorporate the minimum necessary context from the chat history, CONSIDERING ONLY THE HUMAN MESSAGES (messages starting with "Human:").
            b. Formulate a single question that includes this context along with the core of the latest question.
            c. Ensure the modified question remains as close as possible to the original wording.

            If summarizing or modifying:
            a. ONLY USE INFORMATION FROM HUMAN MESSAGES (starting with "Human:"), IGNORE ALL ASSISTANT MESSAGES.
            b. Aim for brevity – typically 1–2 sentences.
            c. Include only key information and context absolutely necessary for understanding.
            d. Remove conversational elements, filler words, and unnecessary details.
            e. Use clear, specific language effective for information retrieval.

            Never introduce new information not present in the human messages or latest question.

            If the latest question is unclear, irrelevant, or doesn't make sense, use it exactly as is without any attempt to interpret or correct it.

            IMPORTANT: When processing the chat history, ONLY READ AND USE MESSAGES THAT BEGIN WITH "Human:". Completely ignore all other messages.

            LATEST USER QUERY:
            {latest_message}

            {"PREVIOUS CONVERSATION CONTEXT:" if previous_conversation else ""}
            {previous_conversation}

            Condensed search query:
        """

        
        # Get the response from the LLM
        response = await llm.acomplete(prompt)
        condensed_query = response.text.strip()
        
        logger.debug(f"Condensed query: {condensed_query}")
        return condensed_query
    except Exception as e:
        logger.error(f"Error condensing messages to query: {e}")
        # Return the latest message in case of error
        return messages[-1] if messages else ""

async def get_vector_search_query(conversation_history: List[Dict[str, Any]], current_message: str, llm: Any) -> str:
    """
    Process conversation history and current message to generate an optimized vector search query.
    
    Args:
        conversation_history: Full conversation history
        current_message: Current user message
        llm: Language model for query condensing
        
    Returns:
        A condensed query string for vector search
    """
    try:
        # Step 1: Filter to get only human message contents (last 6)
        human_message_contents = filter_human_messages(conversation_history)
        
        # Step 2: Add the current message if it's not already in the list
        if current_message not in human_message_contents:
            human_message_contents.append(current_message)
        
        # Step 3: If we have multiple messages, condense them
        if len(human_message_contents) > 1:
            return await condense_human_messages_to_query(human_message_contents, llm)
        # If we only have one message, use it directly
        elif len(human_message_contents) == 1:
            return human_message_contents[0]
        # No messages
        else:
            logger.warning("No human messages found in conversation history")
            return ""
    except Exception as e:
        logger.error(f"Error generating vector search query: {e}")
        # Return current message as fallback
        return current_message
    
def format_conversation_history(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format the conversation history in a structure compatible with LLM API calls.
    
    Args:
        messages: List of message objects from the database
        
    Returns:
        List of formatted messages ready for LLM API consumption
    """
    formatted_messages = []
    
    for message in messages:
        formatted_messages.append({
            "role": message.get("role", "user"),
            "content": message.get("content", "")
        })
        
    return formatted_messages


def log_conversation(conversation_id: str, user_message: str, bot_response: str) -> None:
    """
    Log the conversation for debugging and monitoring purposes.
    
    Args:
        conversation_id: The conversation ID
        user_message: The user's message
        bot_response: The bot's response
    """
    logger.info(f"Conversation {conversation_id}: User: {user_message}")
    logger.info(f"Conversation {conversation_id}: Bot: {bot_response}")

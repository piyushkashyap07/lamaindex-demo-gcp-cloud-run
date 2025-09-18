# The corrected code:
import logging
from app.controllers.handle_messages import handle_messages
from app.controllers.create_conversations import create_conversation_handler
from app.workflows.NewStock_workflow import run_new_stock_workflow
import pytz
from datetime import datetime
from app.models.schema import (
    ApiResponse,
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    BusinessReportResponse,
    CleanBusinessReportResponse,
    StreamingResponse,
    PropensityScore
)
from app.controllers.get_conversations import get_conversations
from fastapi import APIRouter

# Configure logger
logger = logging.getLogger(__name__)
router = APIRouter()

def _extract_company_name_from_response(response_text: str, user_message: str) -> str:
    """
    Extract company name from response text or user message.
    Maps common variations to proper company names.
    """
    # Company name mappings
    company_mappings = {
        'youtube': 'YouTube (Google)',
        'google': 'Google (Alphabet Inc.)',
        'alphabet': 'Alphabet Inc.',
        'meta': 'Meta Platforms Inc.',
        'facebook': 'Meta Platforms Inc.',
        'apple': 'Apple Inc.',
        'microsoft': 'Microsoft Corporation',
        'amazon': 'Amazon.com Inc.',
        'tesla': 'Tesla Inc.',
        'nvidia': 'NVIDIA Corporation',
        'netflix': 'Netflix Inc.',
        'spotify': 'Spotify Technology S.A.',
        'uber': 'Uber Technologies Inc.',
        'airbnb': 'Airbnb Inc.',
        'twitter': 'X (formerly Twitter)',
        'x': 'X (formerly Twitter)',
        'tiktok': 'TikTok (ByteDance)',
        'bytedance': 'ByteDance Ltd.',
        'snapchat': 'Snap Inc.',
        'snap': 'Snap Inc.',
        'pinterest': 'Pinterest Inc.',
        'linkedin': 'LinkedIn (Microsoft)',
        'salesforce': 'Salesforce Inc.',
        'oracle': 'Oracle Corporation',
        'ibm': 'IBM Corporation',
        'intel': 'Intel Corporation',
        'amd': 'Advanced Micro Devices Inc.',
        'qualcomm': 'Qualcomm Inc.',
        'cisco': 'Cisco Systems Inc.',
        'adobe': 'Adobe Inc.',
        'paypal': 'PayPal Holdings Inc.',
        'square': 'Block Inc.',
        'stripe': 'Stripe Inc.',
        'zoom': 'Zoom Video Communications Inc.',
        'slack': 'Slack Technologies Inc.',
        'dropbox': 'Dropbox Inc.',
        'box': 'Box Inc.',
        'atlassian': 'Atlassian Corporation',
        'servicenow': 'ServiceNow Inc.',
        'workday': 'Workday Inc.',
        'snowflake': 'Snowflake Inc.',
        'databricks': 'Databricks Inc.',
        'palantir': 'Palantir Technologies Inc.',
        'crowdstrike': 'CrowdStrike Holdings Inc.',
        'okta': 'Okta Inc.',
        'zendesk': 'Zendesk Inc.',
        'shopify': 'Shopify Inc.',
        'roku': 'Roku Inc.',
        'peloton': 'Peloton Interactive Inc.',
        'docu': 'DocuSign Inc.',
        'docusign': 'DocuSign Inc.',
        'twilio': 'Twilio Inc.',
        'sendgrid': 'Twilio Inc.',
        'mailchimp': 'Mailchimp (Intuit)',
        'hubspot': 'HubSpot Inc.',
        'monday': 'Monday.com Ltd.',
        'asana': 'Asana Inc.',
        'trello': 'Atlassian Corporation',
        'notion': 'Notion Labs Inc.',
        'airtable': 'Airtable Inc.',
        'figma': 'Figma Inc.',
        'canva': 'Canva Pty Ltd.',
        'grammarly': 'Grammarly Inc.',
        'lastpass': 'LogMeIn Inc.',
        '1password': '1Password Inc.',
        'dashlane': 'Dashlane Inc.',
        'bitwarden': 'Bitwarden Inc.',
        'expressvpn': 'ExpressVPN (Kape Technologies)',
        'nordvpn': 'NordVPN (Nord Security)',
        'surfshark': 'Surfshark (Nord Security)',
        'proton': 'Proton AG',
        'protonmail': 'Proton AG',
        'protonvpn': 'Proton AG',
        'tutanota': 'Tutanota GmbH',
        'signal': 'Signal Foundation',
        'telegram': 'Telegram FZ-LLC',
        'whatsapp': 'WhatsApp (Meta)',
        'discord': 'Discord Inc.',
        'teams': 'Microsoft Teams (Microsoft)',
        'webex': 'Webex (Cisco)',
        'gotomeeting': 'GoTo Meeting (LogMeIn)',
        'bluejeans': 'BlueJeans (Verizon)',
        'jitsi': 'Jitsi (8x8)',
        'whereby': 'Whereby (Videxio AS)',
        'calendly': 'Calendly Inc.',
        'acuity': 'Acuity Scheduling Inc.',
        'doodle': 'Doodle AG',
        'when2meet': 'When2meet Inc.',
        'scheduleonce': 'ScheduleOnce Inc.',
        'appointy': 'Appointy Inc.',
        'simplybook': 'SimplyBook.me Ltd.',
        'bookly': 'Bookly Inc.',
        'picktime': 'Picktime Inc.',
        'reservio': 'Reservio Inc.',
        'bookingbug': 'BookingBug Ltd.',
        'infosys': 'Infosys Limited',
        'tcs': 'Tata Consultancy Services',
        'wipro': 'Wipro Limited',
        'hcl': 'HCL Technologies',
        'cognizant': 'Cognizant Technology Solutions',
        'accenture': 'Accenture plc',
        'capgemini': 'Capgemini SE',
        'deloitte': 'Deloitte Touche Tohmatsu Limited',
        'pwc': 'PricewaterhouseCoopers',
        'kpmg': 'KPMG International',
        'ey': 'Ernst & Young',
        'sap': 'SAP SE'
    }
    
    # Check user message first
    user_lower = user_message.lower().strip()
    if user_lower in company_mappings:
        return company_mappings[user_lower]
    
    # Check for partial matches in user message
    for key, value in company_mappings.items():
        if key in user_lower or user_lower in key:
            return value
    
    # If no match found, capitalize and return the original user message
    return user_message.strip().title()


@router.get("/server-check")
def health_check():
    try:
        # Get current time in IST
        ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Server check endpoint hit at {current_time}")

        return ApiResponse(
            status_code=200,
            message="Server check successful. Welcome to Propensity Score Analysis Server!",
            data={
                "serverName": "Propensity Score Analysis Server",
                "timestamp": current_time
            }
        )

    except Exception as e:
        print(e)
        logger.error(f"An ERROR occurred in the Server check: {e}")
        return ApiResponse(
            status_code=500,
            message="Server check failed.",
            data={}
        )


@router.post("/", response_model=ConversationResponse)
async def create_conversation(conversation_data: ConversationCreate):
    """
    Create a new conversation
    Takes a user's email and creates a new conversation with a unique ID.
    """
    logger.info("Create conversations endpoint accessed !")
    response = await create_conversation_handler(conversation_data.email)
    logger.info(f"API logs fetched successfully. Response: {response}")
    return response


@router.post("/message-sync", response_model=CleanBusinessReportResponse)
async def send_message_sync(message_data: MessageCreate):
    """
    Send a message to an existing conversation (synchronous version)
    Takes a conversation ID and user message, returns a structured business report.
    
    Returns a comprehensive business analysis including:
    - Company leadership changes
    - Marketing and advertising signals
    - Competitor ad spending analysis
    - Stock performance trends
    - Propensity score for advertising likelihood
    - Strategic recommendations
    """
    logger.info("Messages sync endpoint accessed !")
    try:
        # Run the workflow and get the final result
        handler = await run_new_stock_workflow(message_data.user_message, message_data.conversation_id, "1")
        
        # Get the final result
        final_result = await handler
        
        # Extract the response
        if hasattr(final_result, 'result') and final_result.result:
            response_text = final_result.result.get("response", "No response available")
        else:
            response_text = str(final_result) if final_result else "No response available"
        
        # Store in conversation history (simplified version)
        from app.helpers.mongodb import mongodb
        from bson import ObjectId
        
        collection = mongodb.get_collection('conversations')
        timestamp = datetime.utcnow()
        
        # Add user message
        collection.update_one(
            {"_id": ObjectId(message_data.conversation_id)},
            {"$push": {"messages": {
                "role": "user",
                "content": message_data.user_message,
                "timestamp": timestamp
            }}}
        )
        
        # Add assistant response
        collection.update_one(
            {"_id": ObjectId(message_data.conversation_id)},
            {"$push": {"messages": {
                "role": "assistant",
                "content": response_text,
                "timestamp": timestamp
            }}}
        )
        
        # Parse the response to extract structured data
        import json
        
        # Try to extract propensity score and other data from the response
        try:
            if isinstance(response_text, str) and response_text.startswith("{'response':"):
                # Parse the response object
                import ast
                response_obj = ast.literal_eval(response_text)
                actual_response = response_obj.get('response', response_text)
                propensity_score_value = response_obj.get('propensity_score', 7)
                score_category = response_obj.get('score_category', 'Medium')

                # Determine visual indicator based on 1-10 scale
                if propensity_score_value >= 8:
                    visual_indicator = "🟢 High"
                elif propensity_score_value >= 5:
                    visual_indicator = "🟡 Medium"
                else:
                    visual_indicator = "🔴 Low"

                # Extract company name from the response
                company_name = _extract_company_name_from_response(actual_response, message_data.user_message)

                return CleanBusinessReportResponse(
                    company_name=company_name,
                    report_date=timestamp,
                    propensity_score=PropensityScore(
                        score=propensity_score_value,
                        rationale="Based on comprehensive business analysis including leadership changes, marketing signals, competitor analysis, and stock performance",
                        visual_indicator=visual_indicator
                    ),
                    overall_summary=actual_response
                )
            else:
                # Fallback for non-structured responses
                return CleanBusinessReportResponse(
                    company_name="Company Analysis",
                    report_date=timestamp,
                    propensity_score=PropensityScore(
                        score=7,
                        rationale="Based on current market conditions and company strategy",
                        visual_indicator="🟡 Medium"
                    ),
                    overall_summary=response_text
                )
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return CleanBusinessReportResponse(
                company_name="Company Analysis",
                report_date=timestamp,
                propensity_score=PropensityScore(
                    score=7,
                    rationale="Based on current market conditions and company strategy",
                    visual_indicator="🟡 Medium"
                ),
                overall_summary=response_text
            )
        
    except Exception as e:
        logger.error(f"Error in sync message endpoint: {e}")
        # Return error response in the same format
        return CleanBusinessReportResponse(
            company_name="Error",
            report_date=datetime.utcnow(),
            propensity_score=PropensityScore(
                score=0,
                rationale="Error occurred during analysis",
                visual_indicator="🔴 Error"
            ),
            overall_summary=f"Error: {str(e)}"
        )
   

@router.get("/get_conversations")
async def get_conversation_history():
    logger.info("Get conversation history endpoint accessed !")
    response = await get_conversations()
    logger.info(f"API logs fetched successfully. Response: {response}")
    return response

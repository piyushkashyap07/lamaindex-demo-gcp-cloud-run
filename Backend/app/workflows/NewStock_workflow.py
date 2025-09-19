import os
import asyncio
import json
import time
from typing import Any, Dict, List, Tuple, Optional
from llama_index.core.workflow import Workflow, step, Context, StartEvent, StopEvent, Event
from llama_index.llms.openai import OpenAI
from llama_index.tools.tavily_research.base import TavilyToolSpec
from llama_index.core.agent.workflow import FunctionAgent
import dotenv
from app.prompts.marketing_signal_prompt import MARKETING_SIGNAL_PROMPT
from app.prompts.leadership_change_prompt import LEADERSHIP_CHANGE_PROMPT
from app.prompts.competitor_ad_spend_prompt import COMPETITOR_AD_SPEND_PROMPT
from app.prompts.three_month_report_prompt import THREE_MONTH_REPORT_PROMPT
from datetime import datetime
import logging
from phoenix.otel import register
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

# Load environment variables
dotenv.load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get OpenTelemetry configuration from environment variables
OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
PHOENIX_PROJECT_NAME = os.getenv("PHOENIX_PROJECT_NAME")

# Register Phoenix tracer
tracer_provider = register(
    endpoint=OTEL_ENDPOINT,
    project_name=PHOENIX_PROJECT_NAME,
    auto_instrument=True
)

# Log tracing configuration details
logger.info("OpenTelemetry Tracing Details")
logger.info(f"|  Phoenix Project: {PHOENIX_PROJECT_NAME}")
logger.info(f"|  Collector Endpoint: {OTEL_ENDPOINT}")
logger.info("|  Transport: HTTP + protobuf")
logger.info("|")

# Instrument LlamaIndex with error handling for already instrumented case
try:
    LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)
    logger.info("Phoenix tracing enabled and LlamaIndex instrumented")
except Exception as e:
    # Already instrumented, continue
    logger.info(f"LlamaIndex already instrumented: {e}")

# Event stubs (now match app.models.event style)
class MarketingSignalEvent(Event):
    user_query: str 
    
class LeadershipChangeEvent(Event):
    user_query: str

class CompetitorAdSpendEvent(Event):
    user_query: str

class ThreeMonthReportEvent(Event):
    user_query: str

class ResponseEvent(Event):
    user_query: str
    response: str

class AnalyzerResponseEvent(Event):
    user_query: str
    rationale: str
    propensity_score: float

class ReportGeneratedEvent(Event):
    user_query: str
    response: str
    propensity_score: float

# Configuration and initialization
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_llm = OpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)
    
if TAVILY_API_KEY:
    tavily_tool = TavilyToolSpec(api_key=TAVILY_API_KEY).to_tool_list()
else:
    tavily_tool = []

search_agent = FunctionAgent(
    tools=tavily_tool,
    llm=openai_llm,
    verbose=True,
    system_prompt="You are a research assistant. Use the search tool to find and summarize relevant information for the user's query."
)

# Stub prompt for analyzer_agent
ANALYZER_PROMPT = """
You are a senior media sales strategist for TelevisaUnivision. Your primary goal is to synthesize market intelligence to determine a brand's Advertiser Opportunity Score for TelevisaUnivision's platform. Today's date is {today}.

Given the detailed findings from four research agents:

1.  Marketing Signal:
    {marketing}

2.  Leadership Change:
    {leadership}

3.  Competitor Ad Spend:
    {competitor}

4.  3-Month Stock Report:
    {report}

Analyze all this information to evaluate the brand's likelihood of becoming a significant advertiser on TelevisaUnivision in the next 3-6 months. Consider the synergy and potential conflicts between these signals.

Your analysis should lead to:

1.  A comprehensive Propensity Score (1-10): This score represents the overall likelihood, where:
    - 9-10: High Propensity - Strong alignment, immediate opportunity.
    - 7-8: Medium-High Propensity - Good alignment, worth focused outreach.
    - 5-6: Medium Propensity - Some alignment, requires specific value proposition.
    - 3-4: Low-Medium Propensity - Limited alignment, requires significant education/long-term nurturing.
    - 1-2: Low Propensity - Poor alignment, not a current priority.

2.  A detailed Rationale: Explain why you assigned this score, citing specific evidence from the agent reports that supports your conclusion. Highlight the most influential factors (positive or negative) and how they relate to the brand's potential for advertising on TelevisaUnivision (e.g., focus on ROI, B2B, lack of traditional media spend, demographic alignment, financial capacity).

3.  Strategic Recommendations for Engagement (2-3 concise bullet points): Based on your analysis, provide actionable advice for the TelevisaUnivision sales team on how to approach this specific advertiser. For example: "Emphasize ROI and performance metrics," "Highlight reach to specific demographics," "Explore B2B partnership opportunities," "Avoid broad brand-building pitches."

Return your answer as a JSON object:
{{
    "propensity_score": <score_integer>,
    "rationale": "<your_detailed_rationale_here>",
    "strategic_recommendations": [
        "<recommendation_1>",
        "<recommendation_2>",
        "<recommendation_3>"
    ]
}}
"""

# Stub prompt for report_agent
REPORT_PROMPT = """
You are tasked with generating a concise, professional business report for TelevisaUnivision stakeholders regarding a potential advertiser. Today's date is {today}.

You will be provided with the following information from an Advertiser Opportunity Analyzer:
- Company Name: {company_name}
- Propensity Score: {propensity_score}
- Rationale: {rationale}
- Strategic Recommendations: {strategic_recommendations} (This will be a list of strings)

Your report must be a maximum of 300 words and adhere to the following structure, using clear, professional language:

---

Business Report: {company_name} Advertiser Opportunity Analysis

1. Executive Summary
Provide a brief, high-level summary of the company's advertising propensity, including the assigned score (1-10) and what it signifies (e.g., "The company has been assigned a propensity score of X, indicating [brief interpretation].").

2. Key Factors Influencing the Score
Elaborate on the primary reasons behind the score, drawing directly from the provided 'rationale'. Focus on the most significant internal and external signals that impact their likelihood to advertise on TelevisaUnivision.

3. Strategic Recommendations for Engagement
Present the actionable recommendations for the TelevisaUnivision sales team, outlining the best approach for engaging with this advertiser. Use the provided 'strategic_recommendations' list directly.

4. Conclusion
Concisely summarize the overall outlook for engaging with this brand, reiterating the main takeaway regarding their potential as a TelevisaUnivision advertiser.

---

Keep the language professional, direct, and actionable for a business audience. Do NOT exceed the 300-word limit.
"""

class NewStockWorkflow(Workflow):
    def _extract_company_name(self, user_query: str) -> str:
        """
        Extract and normalize company name from user query.
        Maps common variations to proper company names.
        """
        query_lower = user_query.lower().strip()
        
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
            'square': 'Block Inc.',
            'roku': 'Roku Inc.',
            'peloton': 'Peloton Interactive Inc.',
            'zoom': 'Zoom Video Communications Inc.',
            'docu': 'DocuSign Inc.',
            'docusign': 'DocuSign Inc.',
            'twilio': 'Twilio Inc.',
            'sendgrid': 'Twilio Inc.',
            'mailchimp': 'Mailchimp (Intuit)',
            'hubspot': 'HubSpot Inc.',
            'salesforce': 'Salesforce Inc.',
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
            'zoom': 'Zoom Video Communications Inc.',
            'webex': 'Webex (Cisco)',
            'gotomeeting': 'GoTo Meeting (LogMeIn)',
            'bluejeans': 'BlueJeans (Verizon)',
            'jitsi': 'Jitsi (8x8)',
            'whereby': 'Whereby (Videxio AS)',
            'calendly': 'Calendly Inc.',
            'acuity': 'Acuity Scheduling Inc.',
            'doodle': 'Doodle AG',
            'when2meet': 'When2meet Inc.',
            'calendly': 'Calendly Inc.',
            'scheduleonce': 'ScheduleOnce Inc.',
            'appointy': 'Appointy Inc.',
            'simplybook': 'SimplyBook.me Ltd.',
            'bookly': 'Bookly Inc.',
            'picktime': 'Picktime Inc.',
            'reservio': 'Reservio Inc.',
            'bookingbug': 'BookingBug Ltd.',
            'acuity': 'Acuity Scheduling Inc.',
            'calendly': 'Calendly Inc.',
            'doodle': 'Doodle AG',
            'when2meet': 'When2meet Inc.',
            'calendly': 'Calendly Inc.',
            'scheduleonce': 'ScheduleOnce Inc.',
            'appointy': 'Appointy Inc.',
            'simplybook': 'SimplyBook.me Ltd.',
            'bookly': 'Bookly Inc.',
            'picktime': 'Picktime Inc.',
            'reservio': 'Reservio Inc.',
            'bookingbug': 'BookingBug Ltd.'
        }
        
        # Check for exact matches first
        if query_lower in company_mappings:
            return company_mappings[query_lower]
        
        # Check for partial matches
        for key, value in company_mappings.items():
            if key in query_lower or query_lower in key:
                return value
        
        # If no match found, capitalize and return the original query
        return user_query.strip().title()
    
    @step(pass_context=True)
    async def trigger_new_stock(self, ctx: Context, ev: StartEvent) -> MarketingSignalEvent | LeadershipChangeEvent | CompetitorAdSpendEvent | ThreeMonthReportEvent:
        """
        Entry point: Triggered when a new stock event occurs.
        Extracts user_query, conversation_id, message_id from ev and passes to agent events.
        """
        user_query = ev.get("user_query")
        conversation_id = ev.get("user_id")
        message_id = str(ev.get("message_id"))  # Convert to string
        ctx.send_event(MarketingSignalEvent(user_query=ev.user_query))
        ctx.send_event(LeadershipChangeEvent(user_query=ev.user_query))
        ctx.send_event(CompetitorAdSpendEvent(user_query=ev.user_query))
        ctx.send_event(ThreeMonthReportEvent(user_query=ev.user_query))

    @step(pass_context=True)
    async def marketing_signal_agent(self, ctx: Context, ev: MarketingSignalEvent) -> ResponseEvent:
        """
        Agent 1: Summarize latest transcript, marketing budget, spend, and financial analysis.
        Uses Gemini LLM and Tavily search tool for research-augmented answers.
        """
        prompt = f"{MARKETING_SIGNAL_PROMPT}\n\nUser Query: {ev.user_query}\n\nPlease research and analyze the marketing signals for the company mentioned in the user query."
        
        try:
            summary = await search_agent.run(prompt)
            return ResponseEvent(user_query=ev.user_query, response=str(summary))
        except Exception as e:
            error_response = f"Error in marketing signal analysis: {str(e)}"
            return ResponseEvent(user_query=ev.user_query, response=error_response)

    @step(pass_context=True)
    async def leadership_change_agent(self, ctx: Context, ev: LeadershipChangeEvent) -> ResponseEvent:
        """
        Agent 2: Detect recent changes in company leadership.
        Uses Gemini LLM and Tavily search tool for research-augmented answers.
        """
        prompt = f"{LEADERSHIP_CHANGE_PROMPT}\n\nUser Query: {ev.user_query}\n\nPlease research and analyze leadership changes for the company mentioned in the user query."
        
        try:
            summary = await search_agent.run(prompt)
            return ResponseEvent(user_query=ev.user_query, response=str(summary))
        except Exception as e:
            error_response = f"Error in leadership change analysis: {str(e)}"
            return ResponseEvent(user_query=ev.user_query, response=error_response)
    
    @step(pass_context=True)
    async def competitor_ad_spend_agent(self, ctx: Context, ev: CompetitorAdSpendEvent) -> ResponseEvent:
        """
        Agent 3: Analyze competitor ad spend.
        Uses Gemini LLM and Tavily search tool for research-augmented answers.
        """
        prompt = f"{COMPETITOR_AD_SPEND_PROMPT}\n\nUser Query: {ev.user_query}\n\nPlease research and analyze competitor ad spending for the company mentioned in the user query."
        
        try:
            summary = await search_agent.run(prompt)
            return ResponseEvent(user_query=ev.user_query, response=str(summary))
        except Exception as e:
            error_response = f"Error in competitor ad spend analysis: {str(e)}"
            return ResponseEvent(user_query=ev.user_query, response=error_response)
    
    @step(pass_context=True)
    async def three_month_report_agent(self, ctx: Context, ev: ThreeMonthReportEvent) -> ResponseEvent:
        """
        Agent 4: Check if the 3-month stock report is positive or not.
        Uses Gemini LLM and Tavily search tool for research-augmented answers.
        """
        prompt = f"{THREE_MONTH_REPORT_PROMPT}\n\nUser Query: {ev.user_query}\n\nPlease research and analyze the 3-month stock performance for the company mentioned in the user query."
        
        try:
            summary = await search_agent.run(prompt)
            return ResponseEvent(user_query=ev.user_query, response=str(summary))
        except Exception as e:
            error_response = f"Error in three month report analysis: {str(e)}"
            return ResponseEvent(user_query=ev.user_query, response=error_response)
    
    @step(pass_context=True)
    async def analyzer_agent(self, ctx: Context, ev: ResponseEvent) -> AnalyzerResponseEvent:
        """
        Analyzer agent: Receives all four agent summaries, computes a propensity score and rationale.
        Uses Gemini LLM for analysis and scoring.
        """
        ready = ctx.collect_events(ev, [ResponseEvent]*4)
        if ready is None:
            return None
            
        today = datetime.now().strftime('%B %d, %Y')
        prompt = ANALYZER_PROMPT.format(
            marketing=ready[0].response,
            leadership=ready[1].response,
            competitor=ready[2].response,
            report=ready[3].response,
            today=today
        )
        
        try:
            response = await openai_llm.acomplete(prompt)
            
            # Try to parse the JSON output for score and rationale
            try:
                # Extract JSON from the response text
                response_text = response.text.strip()
                
                # Look for JSON content between ```json and ``` markers
                if "```json" in response_text and "```" in response_text:
                    start = response_text.find("```json") + 7
                    end = response_text.find("```", start)
                    json_text = response_text[start:end].strip()
                else:
                    # Look for JSON content between { and }
                    start = response_text.find("{")
                    end = response_text.rfind("}") + 1
                    if start != -1 and end != 0:
                        json_text = response_text[start:end]
                    else:
                        json_text = response_text
                
                result = json.loads(json_text)
                score = float(result.get("propensity_score", 0))
                rationale = result.get("rationale", "")
            except Exception as e:
                print(f"JSON parsing error: {e}")
                print(f"Response text: {response.text}")
                score = 0.0
                rationale = response.text.strip()
            
            print(f"Analyzer agent - Parsed score: {score}")
            print(f"Analyzer agent - Parsed rationale: {rationale}")
            
            return AnalyzerResponseEvent(
                propensity_score=score,
                rationale=rationale,
                user_query=ev.user_query,
            )
        except Exception as e:
            error_response = f"Error in analyzer agent: {str(e)}"
            
            return AnalyzerResponseEvent(
                propensity_score=0.0,
                rationale=error_response,
                user_query=ev.user_query,
            )

    @step
    async def report_agent(self, ctx: Context, ev: AnalyzerResponseEvent) -> ReportGeneratedEvent:
        """
        Report agent: Takes the propensity score and rationale, produces a business report.
        Uses Gemini LLM for report formatting.
        """
        today = datetime.now().strftime('%B %d, %Y')
        
        # Extract company name from user query
        company_name = self._extract_company_name(ev.user_query)
        
        prompt = REPORT_PROMPT.format(
            company_name=company_name,
            propensity_score=ev.propensity_score,
            rationale=ev.rationale,
            strategic_recommendations=getattr(ev, 'strategic_recommendations', ''),
            today=today
        )
        print(f"Report agent prompt: {prompt}")
        
        try:
            response = await openai_llm.acomplete(prompt)
            
            return ReportGeneratedEvent(
                user_query=ev.user_query,
                response=response.text.strip(),
                propensity_score=ev.propensity_score
            )
        except Exception as e:
            error_response = f"Error in report generation: {str(e)}"
            
            return ReportGeneratedEvent(
                user_query=ev.user_query,
                response=error_response,
                propensity_score=ev.propensity_score
            )

    @step
    async def final_answer(self, ctx: Context, ev: ReportGeneratedEvent) -> StopEvent:
        """
        Returns the final answer to the user.
        """
        propensity_score = ev.propensity_score
        # Create a visual score indicator for 1-10 scale
        if propensity_score >= 8:
            score_category = "High"
            visual_indicator = "🟢 High"
        elif propensity_score >= 5:
            score_category = "Medium"
            visual_indicator = "🟡 Medium"
        else:
            score_category = "Low"
            visual_indicator = "🔴 Low"
        score_bar = "█" * int(propensity_score) + "░" * (10 - int(propensity_score))
        enhanced_response = f"""
## Propensity Score Analysis: {ev.user_query}

**Score:** {propensity_score}/10 ({score_category} Propensity)
**Visual:** [{score_bar}] {propensity_score * 10}% {visual_indicator}

---

{ev.response}
        """.strip()
        result = {
            "response": enhanced_response,
            "user_query": ev.user_query,
            "propensity_score": propensity_score,
            "score_category": score_category,
            "visual_indicator": visual_indicator
        }
        print(f"Final answer step - Enhanced Response: {enhanced_response}")
        print(f"Final answer step - Result: {result}")
        return StopEvent(result=result)

# Execution of New Stock Workflow
async def run_new_stock_workflow(user_query: str, user_id: str, message_id: str):
    try:
        workflow = NewStockWorkflow(
            timeout=300,  # Increased timeout for potentially multiple LLM calls
        )
        print(f"\n--- Running New Stock Workflow for Query: '{user_query}' ---")
        handler = workflow.run(
            user_query=user_query,
            user_id=user_id,
            message_id=message_id
        )
        return handler
    except Exception as e:
        print(f"Error in New Stock Workflow: {e}")
        # Return a fallback response
        fallback_result = {
            "response": f"## Propensity Score Analysis: {user_query}\n\n**Score:** Unable to calculate\n\n**Error:** The analysis could not be completed due to a technical issue. Please try again later.",
            "user_query": user_query,
            "propensity_score": 0.0,
            "score_category": "Error",
            "visual_indicator": "🔴 Error"
        }
        return type('Handler', (), {'result': fallback_result})()
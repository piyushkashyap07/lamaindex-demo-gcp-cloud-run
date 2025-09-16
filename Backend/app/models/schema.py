from pydantic import BaseModel, Field
from typing import  Any, Optional, List
from datetime import datetime

class ApiResponse(BaseModel):
    status_code: int
    message: str
    data: Any

class SearchQueryModel(BaseModel):
    user_query: str
    thread_id: str

class ConversationQueryModel(BaseModel):
    thread_id: str


class ConversationCreate(BaseModel):
    email: str = Field(..., example="user@example.com", description="User's email address")

class MessageCreate(BaseModel):
    conversation_id: str = Field(..., example="507f1f77bcf86cd799439011", description="MongoDB ObjectId of the conversation")
    user_message: str = Field(..., example="Analyze Meta", description="User's query for business analysis")


class BusinessReportSection(BaseModel):
    """Represents a section of the business report"""
    title: str = Field(..., example="Leadership Changes", description="Section title")
    content: str = Field(..., example="Recent CEO appointment and board restructuring...", description="Detailed content of the section")
    summary: Optional[str] = Field(None, example="Significant leadership changes detected", description="Brief summary of the section")

class PropensityScore(BaseModel):
    """Represents the propensity score with visual indicator"""
    score: int = Field(..., ge=0, le=100, example=35, description="Propensity score from 0-100")
    rationale: str = Field(..., example="Based on current market conditions and company strategy", description="Explanation for the score")
    visual_indicator: str = Field(..., example="🟡 Medium", description="Visual indicator: 🟢 High, 🟡 Medium, 🔴 Low")

class BusinessReportResponse(BaseModel):
    """Complete business report response structure"""
    company_name: str = Field(..., example="Meta Platforms Inc.", description="Name of the analyzed company")
    report_date: datetime = Field(..., example="2025-07-08T05:13:25Z", description="Timestamp of the analysis")
    leadership_changes: Optional[BusinessReportSection] = Field(None, description="Analysis of leadership changes")
    marketing_signals: Optional[BusinessReportSection] = Field(None, description="Analysis of marketing and advertising signals")
    competitor_ad_spending: Optional[BusinessReportSection] = Field(None, description="Analysis of competitor advertising spending")
    stock_performance: Optional[BusinessReportSection] = Field(None, description="Analysis of stock performance")
    propensity_score: PropensityScore = Field(..., description="Propensity score for advertising likelihood")
    overall_summary: str = Field(..., example="Meta shows strong advertising potential...", description="Overall business summary")
    recommendations: Optional[List[str]] = Field(None, example=["Focus on digital advertising", "Monitor competitor spending"], description="Strategic recommendations")

class CleanBusinessReportResponse(BaseModel):
    """Clean business report response structure that excludes null fields"""
    company_name: str = Field(..., example="Meta Platforms Inc.", description="Name of the analyzed company")
    report_date: datetime = Field(..., example="2025-07-08T05:13:25Z", description="Timestamp of the analysis")
    propensity_score: PropensityScore = Field(..., description="Propensity score for advertising likelihood")
    overall_summary: str = Field(..., example="Meta shows strong advertising potential...", description="Overall business summary")
    
    class Config:
        # Exclude fields that are None
        exclude_none = True

class StreamingResponse(BaseModel):
    """Response model for streaming business reports"""
    description: str = "Streaming response containing detailed business analysis with sections for leadership changes, marketing signals, competitor analysis, stock performance, and propensity scoring."

class MessageResponse(BaseModel):
    conversation_id: str = Field(..., example="507f1f77bcf86cd799439011", description="MongoDB ObjectId of the conversation")
    response: str = Field(..., example="Analysis completed...", description="Response content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, example="2025-07-08T05:13:25Z", description="Response timestamp")

class ConversationResponse(BaseModel):
    conversation_id: str = Field(..., example="507f1f77bcf86cd799439011", description="MongoDB ObjectId of the conversation")
    email: str = Field(..., example="user@example.com", description="User's email address")
    created_at: datetime = Field(default_factory=datetime.utcnow, example="2025-07-08T05:13:25Z", description="Conversation creation timestamp")
    status: str = Field(default="active", example="active", description="Conversation status")



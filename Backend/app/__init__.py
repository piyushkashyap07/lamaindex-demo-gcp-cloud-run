from fastapi import FastAPI
from app.log_config import LOGGING_CONFIG
import logging.config
from fastapi.middleware.cors import CORSMiddleware

# Import for lifespan event
from contextlib import asynccontextmanager

# Initialize logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)  # get a logger instance

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Propensity Score Analysis API")
    yield
    # Shutdown
    logger.info("Shutting down Propensity Score Analysis API")

# Create FastAPI app with OpenAPI documentation configuration and lifespan
app = FastAPI(
    title="Propensity Score Analysis API",
    description="""
    ## Propensity Score Analysis API
    
    This API provides comprehensive business analysis and propensity scoring for companies to determine their likelihood of advertising on a platform.
    
    ### Key Features:
    - Business Analysis: Get detailed insights on leadership changes, marketing signals, and competitor activities
    - Propensity Scoring: AI-powered scoring system to predict advertising likelihood
    - Stock Performance Analysis: Comprehensive market performance evaluation
    
    ### Endpoints:
    - `POST /message-sync`: Synchronous business report (structured JSON)
    - `POST /`: Create new conversation
    - `GET /get_conversations`: Retrieve conversation history
    - `GET /server-check`: Health check
    
    ### Example Usage:
    ```bash
    # Synchronous analysis
    curl -X POST "http://localhost:8000/message-sync" \
         -H "Content-Type: application/json" \
         -d '{"conversation_id": "your_conversation_id", "user_message": "Analyze Meta"}'
    ```
    """,
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan  # Add the lifespan manager
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Import and include the router
from app.routes.routes import router
app.include_router(router, prefix="")
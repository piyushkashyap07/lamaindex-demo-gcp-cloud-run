# Propensity Score Analysis - Full Stack Application with Phoenix Tracing

A complete web application for analyzing company propensity scores using AI-powered multi-agent workflows. This application combines a FastAPI backend with a modern HTML/CSS/JavaScript frontend, all containerized for easy deployment with Phoenix tracing for observability.

## 🚀 Quick Start

### Prerequisites
- Docker
- Google Cloud CLI (for deployment)
- API Keys (see Environment Variables section)
- Phoenix service deployed to Google Cloud Run

### 1. Clone and Setup
```bash
git clone <repository-url>
cd google-cloud-run-demo
```

### 2. Environment Configuration
```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your actual API keys
nano .env
```

### 3. Deploy with Docker
```bash
# Build and run the application
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 4. Access the Application
- **Frontend**: http://localhost
- **API Documentation**: http://localhost/docs
- **Health Check**: http://localhost/server-check

## 🏗️ Architecture

### Frontend (HTML/CSS/JavaScript)
- **Location**: `Frontend/`
- **Features**:
  - Modern responsive design
  - Real-time API interactions
  - Toast notifications
  - Loading states and progress indicators
  - Conversation history management

### Backend (FastAPI)
- **Location**: `Backend/`
- **Features**:
  - Multi-agent AI workflow
  - MongoDB integration
  - Vector search capabilities
  - Comprehensive API endpoints

### Unified Deployment
- **Nginx**: Serves frontend and proxies API requests
- **Supervisor**: Manages both Nginx and FastAPI processes
- **Single Container**: Complete application in one Docker image

## 📁 Project Structure

```
google-cloud-run-demo/
├── Frontend/                    # Frontend application
│   ├── index.html              # Main HTML file
│   ├── styles.css              # CSS styling
│   └── script.js               # JavaScript functionality
├── Backend/                     # Backend application
│   ├── app/                     # FastAPI application
│   │   ├── controllers/         # API controllers
│   │   ├── helpers/             # Utility modules
│   │   ├── models/              # Data models
│   │   ├── prompts/             # AI agent prompts
│   │   ├── routes/              # API routes
│   │   └── workflows/           # Multi-agent workflows
│   ├── main.py                  # Application entry point
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile               # Backend Docker config
├── Dockerfile                   # Unified deployment Dockerfile
├── docker-compose.yml           # Docker Compose configuration
├── env.example                  # Environment variables template
└── README.md                    # This file
```

## 🔍 Phoenix Tracing

This application includes enhanced Phoenix tracing for observability of your LlamaIndex workflow agents:

- **Phoenix Service**: Deployed to Google Cloud Run at `https://phoenix-service-538068578089.europe-west4.run.app`
- **OpenInference Integration**: Uses `openinference-instrumentation-llama-index` for comprehensive tracing
- **Automatic Tracing**: All workflow agents are automatically traced with detailed spans
- **Real-time Monitoring**: View traces, performance metrics, and errors
- **Cost Tracking**: Monitor LLM token usage and costs
- **Enhanced Observability**: Better visibility into LlamaIndex operations and agent interactions

### Tracing Setup
The application uses the latest Phoenix tracing configuration:
```python
from phoenix.otel import register
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

# Register Phoenix tracer
tracer_provider = register(
    endpoint=OTEL_ENDPOINT,
    project_name=PHOENIX_PROJECT_NAME,
    auto_instrument=True
)

# Instrument LlamaIndex
LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)
```

### Viewing Traces
1. Run an analysis on your application
2. Open Phoenix UI: https://phoenix-service-538068578089.europe-west4.run.app
3. See complete workflow execution paths and agent performance
4. Monitor detailed LlamaIndex operations and LLM calls

## 🔧 Environment Variables

### Required API Keys
```bash
# Google API Key for Gemini LLM
GOOGLE_API_KEY=your_google_api_key_here

# Tavily API Key for web search
TAVILY_API_KEY=your_tavily_api_key_here

# OpenAI API Key for GPT-4o-mini and embeddings
OPENAI_API_KEY=your_openai_api_key_here

# Pinecone API Key for vector database
PINECONE_API_KEY=your_pinecone_api_key_here
```

### Database Configuration
```bash
# MongoDB connection string
MONGODB_URI=mongodb://localhost:27017

# MongoDB Atlas for vector search (optional)
MONGODB_RAG_URI=your_mongodb_atlas_uri_here
MONGODB_RAG_DB=your_mongodb_rag_database_name
```

### Optional Services
```bash
# Argilla for feedback collection
ARGILLA_API_URL=http://localhost:4535
ARGILLA_API_KEY=your_argilla_api_key_here

# Phoenix Tracing Configuration
PHOENIX_ENABLED=true
PHOENIX_COLLECTOR_ENDPOINT=https://phoenix-service-538068578089.europe-west4.run.app
PHOENIX_PROJECT_NAME=propensity-analysis
```

## 🌐 API Endpoints

### Core Endpoints
- `GET /server-check` - Health check
- `POST /` - Create new conversation
- `POST /message-sync` - Analyze company (synchronous)
- `GET /get_conversations` - Retrieve conversation history

### Frontend Integration
The frontend automatically handles:
- Conversation creation
- Company analysis requests
- Results display with visual indicators
- Error handling and user feedback
- Conversation history management

## 🎯 Usage Examples

### 1. Analyze a Company
1. Open http://localhost in your browser
2. Enter your email address
3. Enter a company name (e.g., "Meta", "Apple", "Tesla")
4. Click "Analyze Company"
5. View the propensity score and detailed analysis

### 2. View Analysis History
- The application automatically saves all analyses
- Click the refresh button to see conversation history
- Each analysis includes company name, score, and summary

### 3. API Integration
```bash
# Create conversation
curl -X POST "http://localhost/" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com"}'

# Analyze company
curl -X POST "http://localhost/message-sync" \
     -H "Content-Type: application/json" \
     -d '{"conversation_id": "conversation_id", "user_message": "Analyze Meta"}'
```

## 🐳 Docker Deployment Options

### Option 1: Docker Compose (Recommended)
```bash
# Full stack with all services
docker-compose up --build

# With local MongoDB
docker-compose --profile local-db up --build

# With Argilla feedback collection
docker-compose --profile argilla up --build
```

### Option 2: Docker Build
```bash
# Build the unified image
docker build -t propensity-analysis-app .

# Run the container
docker run -p 80:80 \
  -e GOOGLE_API_KEY=your_key \
  -e TAVILY_API_KEY=your_key \
  -e OPENAI_API_KEY=your_key \
  -e PINECONE_API_KEY=your_key \
  propensity-analysis-app
```

### Option 3: Google Cloud Run
```bash
# Build and push to Google Container Registry
docker build -t gcr.io/PROJECT_ID/propensity-analysis-app .
docker push gcr.io/PROJECT_ID/propensity-analysis-app

# Deploy to Cloud Run
gcloud run deploy propensity-analysis-app \
  --image gcr.io/PROJECT_ID/propensity-analysis-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 80
```

## 🔍 Features

### Frontend Features
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live progress indicators during analysis
- **Visual Indicators**: Color-coded propensity scores (🟢 High, 🟡 Medium, 🔴 Low)
- **Error Handling**: User-friendly error messages and retry options
- **Conversation Management**: Persistent analysis history
- **Toast Notifications**: Success, error, and info messages

### Backend Features
- **Multi-Agent Analysis**: 4 specialized AI agents analyze different aspects
- **Propensity Scoring**: 1-10 scale with detailed rationale
- **Vector Search**: MongoDB Atlas integration for document retrieval
- **Web Research**: Tavily API integration for real-time data
- **Conversation Persistence**: MongoDB storage for all interactions
- **Comprehensive Logging**: Structured logging for debugging and monitoring

### AI Analysis Agents
1. **Marketing Signal Agent**: Analyzes advertising strategy and budget
2. **Leadership Change Agent**: Detects executive changes and strategic impacts
3. **Competitor Ad Spend Agent**: Evaluates competitive advertising landscape
4. **Three Month Report Agent**: Assesses financial health and stock performance

## 🛠️ Development

### Local Development
```bash
# Backend only
cd Backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Frontend only (serve with any HTTP server)
cd Frontend
python -m http.server 8000
# Access at http://localhost:8000
```

### Testing
```bash
# Test API endpoints
curl http://localhost/server-check

# Test frontend
open http://localhost

# Test workflow with tracing
cd Backend
python test_workflow.py
```

## 📊 Monitoring and Logs

### Application Logs
- **Location**: `./logs/` directory
- **Backend Logs**: `/var/log/supervisor/fastapi_*.log`
- **Nginx Logs**: `/var/log/nginx/*.log`

### Health Monitoring
- **Health Check**: `GET /server-check`
- **Status**: Returns server status and timestamp
- **Monitoring**: Built-in health check endpoint

## 🔒 Security Considerations

### Environment Variables
- Never commit API keys to version control
- Use `.env` files for local development
- Use secure secret management in production

### API Security
- CORS configured for cross-origin requests
- Input validation using Pydantic models
- Error handling prevents information leakage

### Production Deployment
- Use HTTPS in production
- Configure proper firewall rules
- Monitor API usage and rate limiting

## 🚀 Production Deployment

### Google Cloud Run (Recommended)

#### Quick Deployment
```bash
# Use the deployment script (Linux/Mac)
./deploy.sh

# Or use the Windows batch file
deploy.bat
```

#### Manual Deployment
```bash
gcloud run deploy propensity-analysis-app \
  --source . \
  --platform managed \
  --region europe-west4 \
  --allow-unauthenticated \
  --port 80 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars="
    PHOENIX_ENABLED=true,
    PHOENIX_COLLECTOR_ENDPOINT=https://phoenix-service-538068578089.europe-west4.run.app,
    PHOENIX_PROJECT_NAME=propensity-analysis,
    OPENAI_API_KEY=your_key,
    TAVILY_API_KEY=your_key
  "
```

### Local Development
1. Build and push Docker image to GCR
2. Deploy with proper environment variables
3. Configure custom domain (optional)
4. Set up monitoring and alerting

### Other Platforms
- **AWS ECS/Fargate**: Use the Dockerfile directly
- **Azure Container Instances**: Deploy with environment variables
- **Kubernetes**: Use the Docker image with proper configuration

## 📈 Scaling Considerations

### Horizontal Scaling
- Stateless backend design supports multiple instances
- MongoDB can be scaled independently
- Nginx load balancer can distribute traffic

### Performance Optimization
- Vector search caching
- API response caching
- CDN for static frontend assets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the logs in the `logs/` directory
- Test the health check endpoint
- Verify environment variables are set correctly

---

**Built with ❤️ for TelevisaUnivision Business Intelligence**

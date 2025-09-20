# Propensity Score Analysis Platform - Full Stack Application

A complete AI-powered web application for analyzing company propensity scores using multi-agent workflows. This application combines a FastAPI backend with a modern HTML/CSS/JavaScript frontend, deployed on Google Cloud Run with Phoenix tracing for observability.

## 🌐 Live Application

- **Frontend**: [https://propensity-analysis-frontend-538068578089.europe-west4.run.app](https://propensity-analysis-frontend-538068578089.europe-west4.run.app)

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

### 3. Local Development
```bash
# Backend
cd Backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Frontend (in another terminal)
cd Frontend
python -m http.server 8000
# Access at http://localhost:8000
```

### 4. Access the Application
- **Frontend**: http://localhost:8000
- **API Documentation**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/server-check

## 🏗️ Architecture

### System Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Monitoring    │
│   (Cloud Run)   │◄──►│   (Cloud Run)   │◄──►│   (Phoenix)     │
│                 │    │                 │    │                 │
│ • HTML/CSS/JS   │    │ • FastAPI       │    │ • Tracing       │
│ • Responsive    │    │ • LlamaIndex    │    │ • Metrics       │
│ • Real-time     │    │ • Multi-agent   │    │ • Logs          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Data Layer    │
                       │                 │
                       │ • MongoDB       │
                       │ • Pinecone      │
                       │ • Tavily API    │
                       └─────────────────┘
```

### Frontend (HTML/CSS/JavaScript)
- **Location**: `Frontend/`
- **Deployment**: Google Cloud Run
- **Features**:
  - Modern responsive design
  - Real-time API interactions
  - Toast notifications
  - Loading states and progress indicators
  - Conversation history management

### Backend (FastAPI)
- **Location**: `Backend/`
- **Deployment**: Google Cloud Run
- **Features**:
  - Multi-agent AI workflow
  - MongoDB integration
  - Vector search capabilities
  - Comprehensive API endpoints

### Monitoring (Phoenix)
- **Location**: Google Cloud Run
- **Features**:
  - LlamaIndex workflow tracing
  - Performance metrics
  - Error tracking
  - Cost monitoring

## 📁 Project Structure

```
google-cloud-run-demo/
├── Frontend/                    # Frontend application
│   ├── index.html              # Main HTML file
│   ├── styles.css              # CSS styling
│   ├── script.js               # JavaScript functionality
│   ├── Dockerfile              # Frontend Docker config
│   ├── .dockerignore           # Docker ignore file
│   └── README.md               # Frontend documentation
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
│   ├── Dockerfile               # Backend Docker config
│   └── README.md                # Backend documentation
├── venv/                        # Python virtual environment
└── README.md                    # This file
```

## 🔍 Phoenix Tracing

This application includes enhanced Phoenix tracing for observability of your LlamaIndex workflow agents:

- **Phoenix Service**: Deployed to Google Cloud Run
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
2. Open Phoenix UI
3. See complete workflow execution paths and agent performance
4. Monitor detailed LlamaIndex operations and LLM calls

## 🔧 Environment Variables

### Required API Keys
```bash

# Tavily API Key for web search
TAVILY_API_KEY=your_tavily_api_key_here

# OpenAI API Key for GPT-4o-mini and embeddings
OPENAI_API_KEY=your_openai_api_key_here

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

# Phoenix Tracing Configuration
PHOENIX_ENABLED=true
PHOENIX_COLLECTOR_ENDPOINT=https://phoenix-538068578089.us-central1.run.app
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
curl -X POST "" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com"}'

# Analyze company
curl -X POST "" \
     -H "Content-Type: application/json" \
     -d '{"conversation_id": "conversation_id", "user_message": "Analyze Meta"}'
```

## 🐳 Docker Deployment Options

### Option 1: Local Development
```bash
# Backend
cd Backend
docker build -t propensity-analysis-backend .
docker run -p 8080:8080 propensity-analysis-backend

# Frontend
cd Frontend
docker build -t propensity-analysis-frontend .
docker run -p 8000:8080 propensity-analysis-frontend
```

### Option 2: Google Cloud Run (Production)
```bash
# Backend deployment
gcloud builds submit --tag europe-west4-docker.pkg.dev/lamaindex-demo/lama-demo/lamaimg:lamatag ./Backend
gcloud run deploy lamaimg --image europe-west4-docker.pkg.dev/lamaindex-demo/lama-demo/lamaimg:lamatag --platform managed --region europe-west4 --allow-unauthenticated --port 8080

# Frontend deployment
gcloud builds submit --tag europe-west4-docker.pkg.dev/lamaindex-demo/lama-demo-frontend/frontend:latest ./Frontend
gcloud run deploy propensity-analysis-frontend --image europe-west4-docker.pkg.dev/lamaindex-demo/lama-demo-frontend/frontend:latest --platform managed --region europe-west4 --allow-unauthenticated --port 8080
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
curl http://localhost:8080/server-check

# Test frontend
open http://localhost:8000

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
- **Backend Health Check**: `GET /server-check`
- **Frontend Health Check**: `GET /health`
- **Status**: Returns server status and timestamp
- **Monitoring**: Built-in health check endpoints

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
# Backend
gcloud run deploy lamaimg \
  --source ./Backend \
  --platform managed \
  --region europe-west4 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars="
    PHOENIX_ENABLED=true,
    PHOENIX_COLLECTOR_ENDPOINT=,
    PHOENIX_PROJECT_NAME=propensity-analysis,
    OPENAI_API_KEY=your_key,
    TAVILY_API_KEY=your_key
  "

# Frontend
gcloud run deploy propensity-analysis-frontend \
  --source ./Frontend \
  --platform managed \
  --region europe-west4 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300
```

### Production Setup
1. Build and push Docker images to Artifact Registry
2. Deploy with proper environment variables
3. Configure custom domain (optional)
4. Set up monitoring and alerting
5. Configure Phoenix tracing for observability

### Other Platforms
- **AWS ECS/Fargate**: Use the Dockerfile directly
- **Azure Container Instances**: Deploy with environment variables
- **Kubernetes**: Use the Docker image with proper configuration

## 📈 Scaling Considerations

### Horizontal Scaling
- Stateless backend design supports multiple instances
- MongoDB can be scaled independently
- Cloud Run auto-scaling handles traffic distribution

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
- Review the logs in the `logs/` directory
- Test the health check endpoints
- Verify environment variables are set correctly
- Check Phoenix tracing
## 📞 Contact

For technical support or questions about this application, please contact the development team.

---

**Built with ❤️ for TelevisaUnivision Business Intelligence**

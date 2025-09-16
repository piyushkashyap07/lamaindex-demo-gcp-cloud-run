## Propensity Score Analysis API

This API provides comprehensive business analysis and propensity scoring for companies to determine their likelihood of advertising on a platform.

---

### Key Features

- **Business Analysis:** Get detailed insights on leadership changes, marketing signals, and competitor activities.
- **Propensity Scoring:** AI-powered scoring system to predict advertising likelihood.
- **Stock Performance Analysis:** Comprehensive market performance evaluation.
- **Single JSON Storage:** All query and agent data is stored in a single master JSON file for easy access and analysis.

---

### API Keys Required

This application requires the following API keys:

- **Google API Key**: For Gemini LLM integration
- **Tavily API Key**: For web search functionality

#### Getting API Keys

1. **Google API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get your Gemini API key
2. **Tavily API Key**: Visit [Tavily](https://app.tavily.com/home) to get your search API key

> **Note**: If you exceed your free Tavily search limit, visit [https://app.tavily.com/home](https://app.tavily.com/home) to upgrade your plan or get additional credits.

Set these keys in your environment variables or `.env` file:
```bash
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

---

### Project Structure

```
Backend/
│
├── app/
│   ├── __init__.py                # FastAPI app setup and metadata
│   ├── main.py                    # App entry point
│   ├── controllers/               # Business logic for handling requests
│   ├── helpers/                   # Utility modules (data storage, embeddings, MongoDB, etc.)
│   ├── models/                    # Pydantic models and schemas
│   ├── prompts/                   # Agent prompt templates
│   ├── routes/                    # API route definitions
│   ├── workflows/                 # Main workflow logic (multi-agent orchestration)
│   └── log_config.py              # Logging configuration
│
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker support for containerized deployment
├── main.py                        # App entry point (runs FastAPI)
├── logs/                          # Application logs (e.g., app.log)
└── README.md                      # This file
```

---

### Installation

#### 1. **Clone the Repository**
```bash
git clone repoistory
cd propensity-score-poc/Backend
```

#### 2. **Create and Activate a Virtual Environment**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

#### 3. **Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. **Start Argilla (Required for Logging)**
```bash
# Navigate to the helpers directory
cd app/helpers

# Start Argilla using Docker Compose
docker-compose up

# Navigate back to the Backend directory
cd ../..
```

#### 5. **Run the Application**
```bash
python main.py
# The API will be available at http://localhost:8000
```
---

### API Endpoints

- `POST /message-sync`: Synchronous business report (structured JSON)
- `POST /`: Create new conversation
- `GET /get_conversations`: Retrieve conversation history
- `GET /server-check`: Health check

---

### Example Usage

```bash
curl -X POST "http://localhost:8000/message-sync" \
     -H "Content-Type: application/json" \
     -d '{"conversation_id": "your_conversation_id", "user_message": "Analyze Meta"}'
```

---

### Logs

- Application logs are stored in `Backend/logs/app.log` for debugging and monitoring.

---

### Contributing

1. Fork the repository and create a feature branch.
2. Make your changes and add tests if needed.
3. Submit a pull request with a clear description.

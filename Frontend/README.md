# Frontend - Propensity Score Analysis

This is the frontend application for the Propensity Score Analysis platform, built with vanilla HTML, CSS, and JavaScript.

## Features

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Analysis**: Live progress indicators during company analysis
- **Visual Indicators**: Color-coded propensity scores (🟢 High, 🟡 Medium, 🔴 Low)
- **Analysis History**: Persistent conversation history with MongoDB
- **Toast Notifications**: User-friendly success, error, and info messages
- **Modern UI**: Clean, professional interface with smooth animations

## API Integration

The frontend connects to the deployed backend API at:
`https://lama-gcp-arize-backend-538068578089.europe-west4.run.app`

### Endpoints Used

- `GET /server-check` - Health check
- `POST /` - Create new conversation
- `POST /message-sync` - Analyze company (synchronous)
- `GET /get_conversations` - Retrieve conversation history

## Local Development

### Option 1: Simple HTTP Server
```bash
# Navigate to the Frontend directory
cd Frontend

# Start a simple HTTP server
python -m http.server 8000

# Access at http://localhost:8000
```

### Option 2: Node.js HTTP Server
```bash
# Install http-server globally
npm install -g http-server

# Start the server
http-server -p 8000

# Access at http://localhost:8000
```

### Option 3: Live Server (VS Code Extension)
1. Install the "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

## Docker Deployment

### Build the Docker Image
```bash
# Navigate to the Frontend directory
cd Frontend

# Build the Docker image
docker build -t propensity-analysis-frontend .

# Run the container locally
docker run -p 8080:80 propensity-analysis-frontend

# Access at http://localhost:8080
```

### Deploy to Google Cloud Run

#### Option 1: Using gcloud CLI
```bash
# Build and push to Google Container Registry
docker build -t gcr.io/PROJECT_ID/propensity-analysis-frontend .
docker push gcr.io/PROJECT_ID/propensity-analysis-frontend

# Deploy to Cloud Run
gcloud run deploy propensity-analysis-frontend \
  --image gcr.io/PROJECT_ID/propensity-analysis-frontend \
  --platform managed \
  --region europe-west4 \
  --allow-unauthenticated \
  --port 80 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300
```

#### Option 2: Using Cloud Build
```bash
# Submit build to Cloud Build
gcloud builds submit --tag gcr.io/PROJECT_ID/propensity-analysis-frontend

# Deploy to Cloud Run
gcloud run deploy propensity-analysis-frontend \
  --image gcr.io/PROJECT_ID/propensity-analysis-frontend \
  --platform managed \
  --region europe-west4 \
  --allow-unauthenticated
```

## File Structure

```
Frontend/
├── index.html          # Main HTML file
├── script.js           # JavaScript functionality
├── styles.css          # CSS styling
├── Dockerfile          # Docker configuration
├── nginx.conf          # Nginx configuration
├── .dockerignore       # Docker ignore file
└── README.md           # This file
```

## Configuration

### API Base URL
The API base URL is configured in `script.js`:
```javascript
const API_BASE_URL = '';
```

### Environment Variables
No environment variables are required for the frontend as it's a static application.

## Health Check

The application includes a health check endpoint at `/health` that returns "healthy" for monitoring purposes.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- **Gzip Compression**: Enabled for all text-based assets
- **Static Asset Caching**: 1-year cache for static files
- **Minified Assets**: Optimized for production
- **CDN Ready**: Can be deployed behind a CDN

## Security

- **Security Headers**: X-Frame-Options, X-Content-Type-Options, X-XSS-Protection
- **HTTPS Only**: Configured for secure connections
- **CORS**: Handled by the backend API

## Monitoring

- **Health Check**: `/health` endpoint for uptime monitoring
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Console Logging**: Detailed logging for debugging

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure the backend API has proper CORS configuration
2. **API Connection Issues**: Verify the API_BASE_URL is correct
3. **Static File Issues**: Check nginx configuration and file permissions

### Debug Mode

Open browser developer tools to see detailed error messages and API responses.

## Contributing

1. Make changes to the HTML, CSS, or JavaScript files
2. Test locally using one of the development methods above
3. Build and test the Docker image
4. Deploy to Cloud Run for testing
5. Submit pull request with changes

## License

This project is part of the TelevisaUnivision Propensity Score Analysis platform.

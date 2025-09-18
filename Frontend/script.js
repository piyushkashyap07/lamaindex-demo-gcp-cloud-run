// API Configuration
const API_BASE_URL = window.location.origin; // Will work with same-origin deployment

// DOM Elements
const analysisForm = document.getElementById('analysisForm');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const resultsContent = document.getElementById('resultsContent');
const conversationsContent = document.getElementById('conversationsContent');
const refreshBtn = document.getElementById('refreshConversations');
const closeResults = document.getElementById('closeResults');
const toastContainer = document.getElementById('toastContainer');

// Latest Analysis Elements
const latestAnalysisSection = document.getElementById('latestAnalysisSection');
const latestAnalysisContent = document.getElementById('latestAnalysisContent');
const refreshLatestBtn = document.getElementById('refreshLatestBtn');

// State Management
let currentConversationId = null;
let conversations = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadConversations();
    loadLatestAnalysis();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    analysisForm.addEventListener('submit', handleAnalysisSubmit);
    refreshBtn.addEventListener('click', loadConversations);
    closeResults.addEventListener('click', hideResults);
    refreshLatestBtn.addEventListener('click', loadLatestAnalysis);
}

// Handle Analysis Form Submission
async function handleAnalysisSubmit(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const companyQuery = document.getElementById('companyQuery').value;
    
    if (!email || !companyQuery) {
        showToast('Please fill in all fields', 'error');
        return;
    }
    
    try {
        // Show loading state
        showLoading();
        
        // Create conversation first
        const conversation = await createConversation(email);
        currentConversationId = conversation.conversation_id;
        
        // Start analysis
        await analyzeCompany(companyQuery, currentConversationId);
        
    } catch (error) {
        console.error('Analysis error:', error);
        showToast('Analysis failed. Please try again.', 'error');
        hideLoading();
    }
}

// Create Conversation
async function createConversation(email) {
    try {
        const response = await fetch(`${API_BASE_URL}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error creating conversation:', error);
        throw error;
    }
}

// Analyze Company
async function analyzeCompany(companyQuery, conversationId) {
    try {
        const response = await fetch(`${API_BASE_URL}/message-sync`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                conversation_id: conversationId,
                user_message: companyQuery
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayResults(data);
        
        // Refresh conversations and latest analysis
        loadConversations();
        loadLatestAnalysis();
        
    } catch (error) {
        console.error('Error analyzing company:', error);
        throw error;
    }
}

// Display Results
function displayResults(data) {
    hideLoading();
    
    const score = data.propensity_score?.score || 0;
    const rationale = data.propensity_score?.rationale || 'No rationale available';
    const visualIndicator = data.propensity_score?.visual_indicator || '🟡 Medium';
    const companyName = data.company_name || 'Company Analysis';
    const summary = data.overall_summary || 'No summary available';
    
    // Create results HTML
    const resultsHTML = `
        <div class="propensity-score">
            <div class="score-value">${score}/10</div>
            <div class="score-category">${visualIndicator}</div>
            <div class="score-rationale">${rationale}</div>
        </div>
        
        <div class="company-name">${companyName}</div>
        
        <div class="report-content">${summary}</div>
    `;
    
    resultsContent.innerHTML = resultsHTML;
    showResults();
    
    showToast('Analysis completed successfully!', 'success');
}

// Load Conversations
async function loadConversations() {
    try {
        const response = await fetch(`${API_BASE_URL}/get_conversations`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        conversations = data.data?.conversations || [];
        displayConversations();
        
    } catch (error) {
        console.error('Error loading conversations:', error);
        showToast('Failed to load conversation history', 'error');
    }
}

// Display Conversations
function displayConversations() {
    if (conversations.length === 0) {
        conversationsContent.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>No analysis history yet. Start by analyzing a company above.</p>
            </div>
        `;
        return;
    }
    
    // Sort conversations by creation date (newest first)
    const sortedConversations = conversations.sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at)
    );
    
    const conversationsHTML = sortedConversations.slice(0, 10).map(conversation => {
        const messages = conversation.messages || [];
        const messageCount = messages.length;
        const createdDate = new Date(conversation.created_at).toLocaleDateString();
        
        // Find the latest assistant message
        let lastAssistantMessage = null;
        for (let i = messages.length - 1; i >= 0; i--) {
            if (messages[i].role === 'assistant' && messages[i].content) {
                lastAssistantMessage = messages[i];
                break;
            }
        }
        
        // Extract company name from the last assistant message
        let companyName = 'Company Analysis';
        if (lastAssistantMessage && lastAssistantMessage.content) {
            const content = lastAssistantMessage.content;
            const companyMatch = content.match(/## Propensity Score Analysis: (.+?)\n/);
            if (companyMatch) {
                companyName = companyMatch[1];
            }
        }
        
        return `
            <div class="conversation-item">
                <div class="conversation-header">
                    <span class="conversation-email">${conversation.email}</span>
                    <span class="conversation-date">${createdDate}</span>
                </div>
                <div class="conversation-messages">
                    <strong>${companyName}</strong> • ${messageCount} message${messageCount !== 1 ? 's' : ''} • 
                    ${lastAssistantMessage ? `Last: ${lastAssistantMessage.content.substring(0, 80)}${lastAssistantMessage.content.length > 80 ? '...' : ''}` : 'No messages'}
                </div>
            </div>
        `;
    }).join('');
    
    conversationsContent.innerHTML = conversationsHTML;
}

// UI State Management
function showLoading() {
    loadingSection.style.display = 'block';
    resultsSection.style.display = 'none';
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Analyzing...</span>';
    
    // Simulate progress
    const progressFill = document.getElementById('progressFill');
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        progressFill.style.width = progress + '%';
        
        if (progress >= 90) {
            clearInterval(interval);
        }
    }, 200);
}

function hideLoading() {
    loadingSection.style.display = 'none';
    analyzeBtn.disabled = false;
    analyzeBtn.innerHTML = '<i class="fas fa-play"></i><span>Analyze Company</span>';
}

function showResults() {
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function hideResults() {
    resultsSection.style.display = 'none';
}

// Toast Notifications
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
    
    // Click to dismiss
    toast.addEventListener('click', () => {
        toast.remove();
    });
}

// Health Check
async function checkServerHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/server-check`);
        if (response.ok) {
            const data = await response.json();
            console.log('Server health check passed:', data);
        } else {
            console.warn('Server health check failed');
        }
    } catch (error) {
        console.error('Server health check error:', error);
    }
}

// Check server health on load
document.addEventListener('DOMContentLoaded', checkServerHealth);

// Utility Functions
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function truncateText(text, maxLength = 100) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Error Handling
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    showToast('An unexpected error occurred. Please refresh the page.', 'error');
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    showToast('Network error. Please check your connection.', 'error');
});

// Load Latest Analysis
async function loadLatestAnalysis() {
    try {
        const response = await fetch(`${API_BASE_URL}/get_conversations`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        const conversations = data.data?.conversations || [];
        
        if (conversations.length === 0) {
            latestAnalysisSection.style.display = 'none';
            return;
        }
        
        // Find the most recent conversation with messages
        let latestConversation = null;
        let latestMessage = null;
        
        // Sort conversations by creation date (newest first)
        const sortedConversations = conversations.sort((a, b) => 
            new Date(b.created_at) - new Date(a.created_at)
        );
        
        for (const conversation of sortedConversations) {
            const messages = conversation.messages || [];
            if (messages.length > 0) {
                // Sort messages by timestamp (newest first)
                const sortedMessages = messages.sort((a, b) => 
                    new Date(b.timestamp) - new Date(a.timestamp)
                );
                
                for (const message of sortedMessages) {
                    if (message.role === 'assistant' && message.content && message.content.includes('Propensity Score Analysis')) {
                        if (!latestMessage || new Date(message.timestamp) > new Date(latestMessage.timestamp)) {
                            latestConversation = conversation;
                            latestMessage = message;
                        }
                        break; // Found the latest assistant message for this conversation
                    }
                }
            }
        }
        
        if (latestConversation && latestMessage) {
            displayLatestAnalysis(latestConversation, latestMessage);
            latestAnalysisSection.style.display = 'block';
        } else {
            latestAnalysisSection.style.display = 'none';
        }
        
    } catch (error) {
        console.error('Error loading latest analysis:', error);
        latestAnalysisSection.style.display = 'none';
    }
}

// Display Latest Analysis
function displayLatestAnalysis(conversation, message) {
    try {
        // Extract company name and score from the message content
        const content = message.content;
        const companyName = extractCompanyNameFromContent(content);
        const score = extractScoreFromContent(content);
        const rationale = extractRationaleFromContent(content);
        const summary = extractSummaryFromContent(content);
        
        const analysisDate = new Date(message.timestamp).toLocaleDateString();
        
        const latestHTML = `
            <div class="latest-analysis-item" onclick="showFullAnalysis('${conversation._id}', '${message.message_id || ''}')">
                <div class="latest-analysis-item-header">
                    <div class="latest-company-name">${companyName}</div>
                    <div class="latest-analysis-date">${analysisDate}</div>
                </div>
                
                <div class="latest-score-section">
                    <div class="latest-score-value">${score}/10</div>
                    <div class="latest-score-indicator">${getScoreIndicator(score)}</div>
                </div>
                
                <div class="latest-score-rationale">${rationale}</div>
                
                <div class="latest-summary-preview">${summary}</div>
                
                <button class="latest-view-full-btn" onclick="event.stopPropagation(); showFullAnalysis('${conversation._id}', '${message.message_id || ''}')">
                    <i class="fas fa-eye"></i> View Full Analysis
                </button>
            </div>
        `;
        
        latestAnalysisContent.innerHTML = latestHTML;
        
    } catch (error) {
        console.error('Error displaying latest analysis:', error);
        latestAnalysisContent.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>Unable to display latest analysis</p></div>';
    }
}

// Helper functions for extracting data from content
function extractCompanyNameFromContent(content) {
    // Try to extract company name from the content
    const lines = content.split('\n');
    
    // First try: Business Report line
    for (const line of lines) {
        if (line.includes('Business Report:') && line.includes('Advertiser Opportunity Analysis')) {
            const match = line.match(/Business Report: (.+?) Advertiser Opportunity Analysis/);
            if (match) {
                return match[1];
            }
        }
    }
    
    // Second try: Propensity Score Analysis line
    for (const line of lines) {
        if (line.includes('## Propensity Score Analysis:')) {
            const match = line.match(/## Propensity Score Analysis: (.+?)\n/);
            if (match) {
                return match[1];
            }
        }
    }
    
    return 'Company Analysis';
}

function extractScoreFromContent(content) {
    const scoreMatch = content.match(/\*\*Score:\*\* (\d+(?:\.\d+)?)\/10/);
    return scoreMatch ? scoreMatch[1] : '0';
}

function extractRationaleFromContent(content) {
    const rationaleMatch = content.match(/Based on (.+?)(?:\n|$)/);
    return rationaleMatch ? rationaleMatch[1] : 'Analysis completed';
}

function extractSummaryFromContent(content) {
    // Extract the summary section
    const summaryMatch = content.match(/4\. Conclusion\s+(.+?)(?:\n\n|$)/s);
    if (summaryMatch) {
        return summaryMatch[1].substring(0, 200) + '...';
    }
    
    // Fallback to first paragraph
    const lines = content.split('\n').filter(line => line.trim());
    for (const line of lines) {
        if (line.length > 50 && !line.includes('**') && !line.includes('---')) {
            return line.substring(0, 200) + '...';
        }
    }
    
    return 'Analysis summary available in full report...';
}

function getScoreIndicator(score) {
    const numScore = parseFloat(score);
    if (numScore >= 8) return '🟢 High';
    if (numScore >= 5) return '🟡 Medium';
    return '🔴 Low';
}

// Show full analysis (placeholder function)
function showFullAnalysis(conversationId, messageId) {
    // This could open a modal or navigate to a detailed view
    showToast('Full analysis view coming soon!', 'info');
}

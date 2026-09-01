/**
 * AI Advisor Chatbot Frontend
 * Handles communication with the Groq-powered financial advisor API
 */

class FinancialAdvisorChatbot {
    constructor() {
        this.messagesContainer = document.getElementById('messages');
        this.inputField = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-btn');
        this.resetButton = document.getElementById('reset-btn');
        this.tipButton = document.getElementById('tip-btn');
        
        this.initializeEventListeners();
        this.displayWelcomeMessage();
    }
    
    initializeEventListeners() {
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => this.sendMessage());
        }
        
        if (this.inputField) {
            this.inputField.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
        
        if (this.resetButton) {
            this.resetButton.addEventListener('click', () => this.resetConversation());
        }
        
        if (this.tipButton) {
            this.tipButton.addEventListener('click', () => this.getFinancialTip());
        }
    }
    
    displayWelcomeMessage() {
        if (this.messagesContainer) {
            this.addMessage(
                'Welcome to the AI Financial Advisor! I\'m here to help you with investment advice, budget planning, and financial education. What would you like to know today?',
                'bot'
            );
        }
    }
    
    async sendMessage() {
        const message = this.inputField.value.trim();
        
        if (!message) return;
        
        // Display user message
        this.addMessage(message, 'user');
        this.inputField.value = '';
        
        // Show loading indicator
        const loadingId = 'loading-' + Date.now();
        this.addMessage('<span id="' + loadingId + '">⏳ Thinking...</span>', 'bot');
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            // Remove loading indicator
            const loadingElement = document.getElementById(loadingId);
            if (loadingElement) {
                loadingElement.parentElement.remove();
            }
            
            if (data.success) {
                this.addMessage(data.response, 'bot');
            } else {
                this.addMessage('Sorry, I encountered an error: ' + data.message, 'bot');
            }
        } catch (error) {
            // Remove loading indicator
            const loadingElement = document.getElementById(loadingId);
            if (loadingElement) {
                loadingElement.parentElement.remove();
            }
            
            this.addMessage('Error: Unable to connect to the advisor. Please try again.', 'bot');
            console.error('Chat error:', error);
        }
    }
    
    async resetConversation() {
        if (!confirm('Are you sure you want to clear the conversation history?')) {
            return;
        }
        
        try {
            const response = await fetch('/api/chat/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Clear messages and display welcome message
                if (this.messagesContainer) {
                    this.messagesContainer.innerHTML = '';
                }
                this.displayWelcomeMessage();
            } else {
                this.addMessage('Failed to reset conversation: ' + data.message, 'bot');
            }
        } catch (error) {
            this.addMessage('Error: Unable to reset conversation.', 'bot');
            console.error('Reset error:', error);
        }
    }
    
    async getFinancialTip() {
        this.addMessage('💡 Getting a financial tip for you...', 'bot');
        
        try {
            const response = await fetch('/api/chat/tip', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addMessage('💰 ' + data.tip, 'bot');
            } else {
                this.addMessage('Unable to fetch financial tip: ' + data.message, 'bot');
            }
        } catch (error) {
            this.addMessage('Error: Unable to fetch financial tip.', 'bot');
            console.error('Tip error:', error);
        }
    }
    
    addMessage(message, sender) {
        if (!this.messagesContainer) return;
        
        const messageElement = document.createElement('div');
        messageElement.className = 'message ' + sender + '-message';
        
        const contentElement = document.createElement('div');
        contentElement.className = 'message-content';
        contentElement.innerHTML = message;
        
        messageElement.appendChild(contentElement);
        this.messagesContainer.appendChild(messageElement);
        
        // Auto-scroll to bottom
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
}

// Initialize chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const chatbotContainer = document.getElementById('chatbot-container');
    if (chatbotContainer) {
        new FinancialAdvisorChatbot();
    }
});

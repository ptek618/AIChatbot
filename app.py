from flask import Flask, request, jsonify, render_template_string
from twilio.twiml.messaging_response import MessagingResponse
from chatbot_engine import ProTekChatbot
from admin_gui import AdminGUI
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
chatbot = ProTekChatbot()
admin_gui = AdminGUI(app)

@app.route("/")
def home():
    return jsonify({
        "message": "🌐 ProTek AI Chatbot is running",
        "version": "2.0",
        "endpoints": {
            "sms": "/sms",
            "chat": "/chat",
            "chat_api": "/chat/message"
        }
    })

@app.route("/sms", methods=["POST"])
def sms_reply():
    """Handle incoming SMS messages via Twilio"""
    incoming_msg = request.form.get("Body", "").strip()
    phone_number = request.form.get("From", "")
    resp = MessagingResponse()

    if not incoming_msg:
        resp.message("🤖 I didn't receive your message. Please try again.")
        return str(resp)

    response_text = chatbot.process_message(phone_number, incoming_msg)
    resp.message(response_text)

    return str(resp)

@app.route("/chat")
def chat_interface():
    """Serve the web chat interface"""
    return render_template_string(CHAT_HTML_TEMPLATE)

@app.route("/chat/message", methods=["POST"])
def chat_message():
    """Handle web chat messages"""
    data = request.get_json()
    message = data.get("message", "").strip()
    session_id = data.get("session_id", "web_user_default")
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    response_text = chatbot.process_message(session_id, message)
    
    return jsonify({
        "response": response_text,
        "session_id": session_id
    })

@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "protek-ai-chatbot"})

CHAT_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ProTek Internet Support - AI Chat</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .chat-container {
            width: 100%;
            max-width: 900px;
            height: 85vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #2E7D32, #4CAF50);
            color: white;
            padding: 25px;
            text-align: center;
            position: relative;
        }
        
        .chat-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1.5" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="80" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
        }
        
        .chat-header h1 {
            font-size: 28px;
            margin-bottom: 8px;
            position: relative;
            z-index: 1;
        }
        
        .chat-header p {
            opacity: 0.95;
            font-size: 16px;
            position: relative;
            z-index: 1;
        }
        
        .chat-messages {
            flex: 1;
            padding: 25px;
            overflow-y: auto;
            background: #f8f9fa;
            scroll-behavior: smooth;
        }
        
        .message {
            margin-bottom: 20px;
            display: flex;
            align-items: flex-start;
            animation: fadeIn 0.3s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message-content {
            max-width: 75%;
            padding: 15px 20px;
            border-radius: 20px;
            white-space: pre-wrap;
            line-height: 1.5;
            font-size: 15px;
            position: relative;
        }
        
        .message.bot .message-content {
            background: linear-gradient(135deg, #e3f2fd, #bbdefb);
            color: #1565c0;
            border-bottom-left-radius: 6px;
            border: 1px solid #90caf9;
        }
        
        .message.user .message-content {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            border-bottom-right-radius: 6px;
            box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
        }
        
        .typing-indicator {
            display: none;
            padding: 15px 25px;
            color: #666;
            font-style: italic;
            background: #f0f0f0;
            border-radius: 10px;
            margin: 0 25px 10px;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.7; }
            50% { opacity: 1; }
        }
        
        .chat-input-container {
            padding: 25px;
            background: white;
            border-top: 2px solid #e0e0e0;
        }
        
        .chat-input-form {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        
        .chat-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 30px;
            font-size: 16px;
            outline: none;
            transition: all 0.3s ease;
            background: #f8f9fa;
        }
        
        .chat-input:focus {
            border-color: #4CAF50;
            background: white;
            box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
        }
        
        .send-button {
            padding: 15px 25px;
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        }
        
        .send-button:hover {
            background: linear-gradient(135deg, #45a049, #388e3c);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
        }
        
        .send-button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .status-indicator {
            position: absolute;
            top: 10px;
            right: 15px;
            width: 12px;
            height: 12px;
            background: #4CAF50;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            .chat-container {
                height: 95vh;
                border-radius: 15px;
            }
            
            .chat-header {
                padding: 20px;
            }
            
            .chat-header h1 {
                font-size: 24px;
            }
            
            .chat-messages {
                padding: 20px;
            }
            
            .message-content {
                max-width: 85%;
                padding: 12px 16px;
                font-size: 14px;
            }
            
            .chat-input-container {
                padding: 20px;
            }
            
            .chat-input {
                padding: 12px 16px;
                font-size: 16px;
            }
            
            .send-button {
                padding: 12px 20px;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <div class="status-indicator"></div>
            <h1>🌐 ProTek Internet Support</h1>
            <p>24/7 AI-Powered Customer Support • Always Here to Help</p>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot">
                <div class="message-content">
👋 Welcome to ProTek Internet Support! I'm your AI assistant, available 24/7 to help you with any internet-related issues.

To provide you with the best support, please let me know what type of customer you are:

🏢 **Business** - Commercial internet services
🏠 **Residential** - Home internet services  
🏢 **Enterprise** - Large-scale business solutions
🔧 **Northbridge IT Services** - Managed IT support

Just type your customer type to get started!
                </div>
            </div>
        </div>
        
        <div class="typing-indicator" id="typingIndicator">
            🤖 ProTek Support is typing...
        </div>
        
        <div class="chat-input-container">
            <form class="chat-input-form" id="chatForm">
                <input 
                    type="text" 
                    class="chat-input" 
                    id="messageInput" 
                    placeholder="Type your message here..."
                    autocomplete="off"
                    required
                >
                <button type="submit" class="send-button" id="sendButton">
                    Send 📤
                </button>
            </form>
        </div>
    </div>

    <script>
        const chatMessages = document.getElementById('chatMessages');
        const chatForm = document.getElementById('chatForm');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const typingIndicator = document.getElementById('typingIndicator');
        
        let sessionId = 'web_' + Math.random().toString(36).substr(2, 12) + '_' + Date.now();
        
        function addMessage(content, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;
            
            messageDiv.appendChild(contentDiv);
            chatMessages.appendChild(messageDiv);
            
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function showTyping() {
            typingIndicator.style.display = 'block';
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function hideTyping() {
            typingIndicator.style.display = 'none';
        }
        
        async function sendMessage(message) {
            try {
                showTyping();
                sendButton.disabled = true;
                sendButton.textContent = 'Sending...';
                
                // Get the current origin without credentials for the fetch request
                const baseUrl = window.location.protocol + '//' + window.location.host;
                
                const response = await fetch(baseUrl + '/chat/message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        session_id: sessionId
                    })
                });
                
                const data = await response.json();
                
                hideTyping();
                
                if (response.ok) {
                    addMessage(data.response, false);
                } else {
                    addMessage('❌ Sorry, there was an error processing your message. Please try again or contact support directly.', false);
                }
            } catch (error) {
                hideTyping();
                addMessage('🔌 Connection error. Please check your internet connection and try again.', false);
            } finally {
                sendButton.disabled = false;
                sendButton.textContent = 'Send 📤';
            }
        }
        
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const message = messageInput.value.trim();
            if (!message) return;
            
            addMessage(message, true);
            messageInput.value = '';
            
            await sendMessage(message);
        });
        
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
        
        // Auto-focus on input
        messageInput.focus();
        
        // Add some visual feedback
        messageInput.addEventListener('input', () => {
            if (messageInput.value.trim()) {
                sendButton.style.background = 'linear-gradient(135deg, #4CAF50, #45a049)';
            } else {
                sendButton.style.background = '#ccc';
            }
        });
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

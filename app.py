from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.twiml.messaging_response import MessagingResponse
import subprocess
import threading
import os
from dotenv import load_dotenv
import logging
from customer_data import CustomerDatabase
from sonar_client import SonarClient

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

customer_db = CustomerDatabase()
sonar_client = SonarClient()

ESCALATION_KEYWORDS = [
    keyword.strip().lower() 
    for keyword in os.getenv('ESCALATION_KEYWORDS', '').split(',')
    if keyword.strip()
]

@app.route("/")
def home():
    return jsonify({"message": "✅ ProTek Chatbot is running. I hope this works!"})

@app.route("/git-pull", methods=["POST"])
def git_pull():
    try:
        result = subprocess.run(["git", "pull"], capture_output=True, text=True, cwd="/opt/protek-chatbot")
        output = result.stdout.strip()
        error_output = result.stderr.strip()

        def restart_service():
            subprocess.run(["sudo", "systemctl", "restart", "protek-chatbot"])

        threading.Thread(target=restart_service).start()

        return jsonify({
            "output": output or error_output,
            "status": "success"
        }), 200

    except Exception as e:
        return jsonify({"output": str(e), "status": "error"}), 500

def detect_escalation(message: str) -> bool:
    """Check if message contains escalation keywords"""
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in ESCALATION_KEYWORDS)

def handle_escalation(phone_number: str, message: str, customer_data: dict) -> str:
    """Handle escalation by creating Sonar ticket"""
    customer_name = customer_data.get('name', 'Unknown Customer')
    customer_type = customer_db.get_customer_type(customer_data)
    
    subject = f"Customer Escalation - {customer_name} ({customer_type})"
    description = f"""
Customer escalation received via SMS chatbot.

Customer: {customer_name}
Phone: {phone_number}
Customer Type: {customer_type}
Account ID: {customer_data.get('account_id', 'N/A')}

Original Message: {message}

Hardware Information:
{customer_db.get_customer_hardware(customer_data)}
"""
    
    ticket = sonar_client.create_internal_ticket(
        subject=subject,
        description=description,
        customer_data=customer_data,
        priority=os.getenv('DEFAULT_TICKET_PRIORITY', 'MEDIUM'),
        status=os.getenv('DEFAULT_TICKET_STATUS', 'OPEN')
    )
    
    if ticket:
        logger.info(f"Created ticket {ticket.get('id')} for customer {customer_name}")
        return f"🎫 I've escalated your issue to our support team. Ticket #{ticket.get('id')} has been created. A technician will contact you soon."
    else:
        logger.error(f"Failed to create ticket for customer {customer_name}")
        return "⚠️ I'm having trouble escalating your issue right now. Please call our support line directly."

@app.route("/chat/message", methods=["POST"])
def chat_message():
    """Web chat endpoint that bridges to SMS logic with Sonar integration"""
    from flask import request, jsonify
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id', '')
        
        logger.info(f"Received web chat message from session {session_id}: {message}")
        
        if not message:
            return jsonify({"response": "Please enter a message."}), 400
        
        import re
        phone_pattern = r'[\+]?[1]?[\s\-\(\)]?(\d{3})[\s\-\(\)]?(\d{3})[\s\-]?(\d{4})'
        phone_match = re.search(phone_pattern, message)
        
        if phone_match or any(char.isdigit() for char in message) and len([c for c in message if c.isdigit()]) >= 10:
            phone_number = message
            customer_data = customer_db.authenticate_customer(phone_number)
            
            if customer_data:
                customer_name = customer_data.get('name', 'Customer')
                customer_type = customer_db.get_customer_type(customer_data)
                response = f"👋 Hello {customer_name}! I've authenticated you as a {customer_type.title()} customer. How can I help you today?\n\n• Ask about 'wifi password'\n• Ask about 'hardware' or 'equipment'\n• Report issues (I'll escalate urgent problems)\n• Say 'help' for more options"
                return jsonify({"response": response})
            else:
                return jsonify({"response": "🚫 Sorry, I don't recognize that phone number in our system. Please contact support to verify your account or update your contact information."})
        
        if 'phone' not in session_id.lower() and not any(word in message.lower() for word in ['hello', 'hi', 'help']):
            return jsonify({"response": "👋 Welcome to ProTek Internet Support! To provide personalized assistance, please enter your phone number (the one associated with your account)."})
        
        message_lower = message.lower()
        if any(word in message_lower for word in ['hello', 'hi', 'help', 'start']):
            return jsonify({"response": "👋 Welcome to ProTek Internet Support! I'm your AI assistant, available 24/7 to help you with any internet-related issues.\n\nTo get started, please enter your phone number (the one associated with your ProTek account) so I can authenticate you and provide personalized support."})
        
        return jsonify({"response": "🔐 To assist you with account-specific information, please first enter your phone number associated with your ProTek account."})
        
    except Exception as e:
        logger.error(f"Error in chat_message: {e}")
        return jsonify({"response": "❌ Sorry, there was an error processing your message. Please try again or contact support directly."}), 500

@app.route("/chat/authenticated", methods=["POST"])
def chat_authenticated():
    """Handle authenticated chat messages after phone number verification"""
    from flask import request, jsonify
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        phone_number = data.get('phone_number', '').strip()
        session_id = data.get('session_id', '')
        
        logger.info(f"Received authenticated chat message from {phone_number}: {message}")
        
        if not phone_number:
            return jsonify({"response": "🔐 Phone number required for authenticated requests."}), 400
        
        customer_data = customer_db.authenticate_customer(phone_number)
        
        if not customer_data:
            return jsonify({"response": "🚫 Sorry, I don't recognize your phone number in our system. Please contact support to verify your account or update your contact information."})
        
        customer_name = customer_data.get('name', 'Customer')
        message_lower = message.lower()
        
        if detect_escalation(message):
            escalation_response = handle_escalation(phone_number, message, customer_data)
            return jsonify({"response": escalation_response})
        
        if any(word in message_lower for word in ['wifi', 'password', 'network']):
            wifi_password = customer_db.get_wifi_password(customer_data)
            if wifi_password:
                response = f"🔐 Hi {customer_name}! Your WiFi password is: {wifi_password}"
            else:
                response = f"🚫 Hi {customer_name}! You're not authorized to receive WiFi credentials via this channel. Please contact support."
            return jsonify({"response": response})
        
        if any(word in message_lower for word in ['hardware', 'equipment', 'modem', 'router']):
            hardware = customer_db.get_customer_hardware(customer_data)
            if hardware:
                hardware_info = "\n".join([f"{k.title()}: {v}" for k, v in hardware.items()])
                response = f"🔧 Hi {customer_name}! Your equipment:\n{hardware_info}"
            else:
                response = f"📋 Hi {customer_name}! No hardware information found. Please contact support."
            return jsonify({"response": response})
        
        if "hi" in message_lower or "hello" in message_lower:
            response = f"👋 Hello {customer_name}! This is the ProTek Chatbot. How can I help you today?"
        elif "help" in message_lower:
            customer_type = customer_db.get_customer_type(customer_data)
            response = f"🛠️ Hi {customer_name}! I can help with:\n• WiFi passwords\n• Equipment info\n• Service issues\n• Account: {customer_type.title()}"
        else:
            response = f"🤖 Hi {customer_name}! I didn't understand that. Try asking about 'wifi', 'hardware', or say 'help'. For urgent issues, use words like 'urgent' or 'escalate'."
        
        return jsonify({"response": response})
        
    except Exception as e:
        logger.error(f"Error in chat_authenticated: {e}")
        return jsonify({"response": "❌ Sorry, there was an error processing your message. Please try again or contact support directly."}), 500

@app.route("/chat")
def chat_interface():
    """Enhanced web interface for testing the chatbot with Sonar integration"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ProTek Internet Support - AI Chat</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .chat-container {
                width: 90%;
                max-width: 800px;
                height: 80vh;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            
            .chat-header {
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white;
                padding: 20px;
                text-align: center;
            }
            
            .chat-header h1 {
                margin: 0;
                font-size: 24px;
                font-weight: 600;
            }
            
            .chat-header p {
                margin: 5px 0 0 0;
                opacity: 0.9;
                font-size: 14px;
            }
            
            .chat-messages {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                background-color: #f8f9fa;
            }
            
            .message {
                margin-bottom: 15px;
                display: flex;
                align-items: flex-start;
            }
            
            .message.user {
                justify-content: flex-end;
            }
            
            .message-content {
                max-width: 70%;
                padding: 12px 16px;
                border-radius: 18px;
                font-size: 14px;
                line-height: 1.4;
                white-space: pre-wrap;
            }
            
            .message.bot .message-content {
                background-color: #e9ecef;
                color: #333;
                border-bottom-left-radius: 4px;
            }
            
            .message.user .message-content {
                background: linear-gradient(135deg, #007bff, #0056b3);
                color: white;
                border-bottom-right-radius: 4px;
            }
            
            .typing-indicator {
                display: none;
                padding: 12px 16px;
                background-color: #e9ecef;
                border-radius: 18px;
                border-bottom-left-radius: 4px;
                max-width: 70%;
                margin-bottom: 15px;
            }
            
            .typing-dots {
                display: flex;
                align-items: center;
                gap: 4px;
            }
            
            .typing-dots span {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: #6c757d;
                animation: typing 1.4s infinite ease-in-out;
            }
            
            .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
            .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
            
            @keyframes typing {
                0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
                30% { transform: translateY(-10px); opacity: 1; }
            }
            
            .chat-input {
                padding: 20px;
                background: white;
                border-top: 1px solid #e9ecef;
            }
            
            .input-container {
                display: flex;
                gap: 10px;
                align-items: flex-end;
            }
            
            .message-input {
                flex: 1;
                padding: 12px 16px;
                border: 2px solid #e9ecef;
                border-radius: 20px;
                font-size: 14px;
                resize: none;
                outline: none;
                transition: border-color 0.2s;
                max-height: 100px;
                min-height: 44px;
            }
            
            .message-input:focus {
                border-color: #007bff;
            }
            
            .send-button {
                background: linear-gradient(135deg, #007bff, #0056b3);
                color: white;
                border: none;
                border-radius: 50%;
                width: 44px;
                height: 44px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: transform 0.2s;
                font-size: 16px;
            }
            
            .send-button:hover {
                transform: scale(1.05);
            }
            
            .send-button:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
            }
            
            .auth-status {
                padding: 10px 20px;
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                margin-bottom: 10px;
                font-size: 14px;
            }
            
            .auth-status.authenticated {
                background: #d1edff;
                border-left-color: #007bff;
            }
            
            .examples {
                margin-top: 20px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 10px;
                font-size: 12px;
                color: #6c757d;
            }
            
            .examples h4 {
                margin: 0 0 10px 0;
                color: #495057;
            }
            
            .examples ul {
                margin: 0;
                padding-left: 15px;
            }
            
            .examples li {
                margin: 5px 0;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <h1>🌐 ProTek Internet Support</h1>
                <p>24/7 AI-Powered Customer Support • Always Here to Help</p>
            </div>
            
            <div id="authStatus" class="auth-status">
                📱 Please enter your phone number to get started
            </div>
            
            <div id="chatMessages" class="chat-messages">
                <div class="message bot">
                    <div class="message-content">
                        👋 Welcome to ProTek Internet Support! I'm your AI assistant, available 24/7 to help you with any internet-related issues.

To provide you with the best support, please enter your phone number (the one associated with your ProTek account) so I can authenticate you and provide personalized assistance.
                    </div>
                </div>
                
                <div class="examples">
                    <h4>📞 Test Phone Numbers (from Sonar):</h4>
                    <ul>
                        <li><strong>6186944239</strong> - Kelley Powell (Residential)</li>
                        <li><strong>6189226759</strong> - Cameron McCurdy (Residential)</li>
                        <li><strong>6189974769</strong> - Accu-Grow Lawn & Tree Care (Commercial)</li>
                    </ul>
                    
                    <h4>💬 Example Messages to Try After Authentication:</h4>
                    <ul>
                        <li>"wifi password" - Get your WiFi credentials</li>
                        <li>"hardware" - View your equipment info</li>
                        <li>"urgent help my internet is down" - Escalate to support</li>
                        <li>"help" - See all available options</li>
                    </ul>
                </div>
            </div>
            
            <div class="typing-indicator" id="typingIndicator">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
            
            <div class="chat-input">
                <form id="chatForm">
                    <div class="input-container">
                        <textarea id="messageInput" class="message-input" 
                                placeholder="Type your message here..." 
                                rows="1"></textarea>
                        <button type="submit" id="sendButton" class="send-button">📤</button>
                    </div>
                </form>
            </div>
        </div>

        <script>
            const chatMessages = document.getElementById('chatMessages');
            const chatForm = document.getElementById('chatForm');
            const messageInput = document.getElementById('messageInput');
            const sendButton = document.getElementById('sendButton');
            const typingIndicator = document.getElementById('typingIndicator');
            const authStatus = document.getElementById('authStatus');
            
            let sessionId = 'web_' + Math.random().toString(36).substr(2, 12) + '_' + Date.now();
            let isAuthenticated = false;
            let customerPhone = '';
            let customerName = '';
            
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
            
            function updateAuthStatus(phone = '', name = '') {
                if (phone && name) {
                    authStatus.textContent = `✅ Authenticated as ${name} (${phone})`;
                    authStatus.className = 'auth-status authenticated';
                    isAuthenticated = true;
                    customerPhone = phone;
                    customerName = name;
                } else {
                    authStatus.textContent = '📱 Please enter your phone number to get started';
                    authStatus.className = 'auth-status';
                    isAuthenticated = false;
                    customerPhone = '';
                    customerName = '';
                }
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
                    sendButton.textContent = '⏳';
                    
                    // Get the base URL without credentials for fetch requests
                    const currentUrl = window.location.href;
                    const baseUrl = currentUrl.substring(0, currentUrl.lastIndexOf('/'));
                    
                    let endpoint = baseUrl + '/chat/message';
                    let payload = {
                        message: message,
                        session_id: sessionId
                    };
                    
                    // If authenticated, use the authenticated endpoint
                    if (isAuthenticated) {
                        endpoint = baseUrl + '/chat/authenticated';
                        payload.phone_number = customerPhone;
                    }
                    
                    const response = await fetch(endpoint, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(payload)
                    });
                    
                    const data = await response.json();
                    
                    hideTyping();
                    
                    if (response.ok) {
                        addMessage(data.response, false);
                        
                        // Check if this was a successful phone authentication
                        if (!isAuthenticated && data.response.includes('authenticated you as')) {
                            // Extract customer name from response
                            const nameMatch = data.response.match(/Hello ([^!]+)!/);
                            if (nameMatch) {
                                updateAuthStatus(message, nameMatch[1]);
                            }
                        }
                    } else {
                        addMessage('❌ Sorry, there was an error processing your message. Please try again or contact support directly.', false);
                    }
                } catch (error) {
                    hideTyping();
                    addMessage('🔌 Connection error. Please check your internet connection and try again.', false);
                } finally {
                    sendButton.disabled = false;
                    sendButton.textContent = '📤';
                }
            }
            
            chatForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const message = messageInput.value.trim();
                if (!message) return;
                
                addMessage(message, true);
                messageInput.value = '';
                messageInput.style.height = 'auto';
                
                await sendMessage(message);
            });
            
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    chatForm.dispatchEvent(new Event('submit'));
                }
            });
            
            // Auto-resize textarea
            messageInput.addEventListener('input', () => {
                messageInput.style.height = 'auto';
                messageInput.style.height = Math.min(messageInput.scrollHeight, 100) + 'px';
            });
            
            // Auto-focus on input
            messageInput.focus();
        </script>
    </body>
    </html>
    '''

@app.route("/sms", methods=["POST"])
def sms_reply():
    incoming_msg = request.form.get("Body", "").strip()
    phone_number = request.form.get("From", "").strip()
    resp = MessagingResponse()
    
    logger.info(f"Received SMS from {phone_number}: {incoming_msg}")
    
    customer_data = customer_db.authenticate_customer(phone_number)
    
    if not customer_data:
        resp.message("🚫 Sorry, I don't recognize your phone number in our system. Please contact support to verify your account or update your contact information.")
        return str(resp)
    
    customer_name = customer_data.get('name', 'Customer')
    message_lower = incoming_msg.lower()
    
    if detect_escalation(incoming_msg):
        escalation_response = handle_escalation(phone_number, incoming_msg, customer_data)
        resp.message(escalation_response)
        return str(resp)
    
    if any(word in message_lower for word in ['wifi', 'password', 'network']):
        wifi_password = customer_db.get_wifi_password(customer_data)
        if wifi_password:
            resp.message(f"🔐 Hi {customer_name}! Your WiFi password is: {wifi_password}")
        else:
            resp.message(f"🚫 Hi {customer_name}! You're not authorized to receive WiFi credentials via this channel. Please contact support.")
        return str(resp)
    
    if any(word in message_lower for word in ['hardware', 'equipment', 'modem', 'router']):
        hardware = customer_db.get_customer_hardware(customer_data)
        if hardware:
            hardware_info = "\n".join([f"{k.title()}: {v}" for k, v in hardware.items()])
            resp.message(f"🔧 Hi {customer_name}! Your equipment:\n{hardware_info}")
        else:
            resp.message(f"📋 Hi {customer_name}! No hardware information found. Please contact support.")
        return str(resp)
    
    if "hi" in message_lower or "hello" in message_lower:
        resp.message(f"👋 Hello {customer_name}! This is the ProTek Chatbot. How can I help you today?")
    elif "help" in message_lower:
        customer_type = customer_db.get_customer_type(customer_data)
        resp.message(f"🛠️ Hi {customer_name}! I can help with:\n• WiFi passwords\n• Equipment info\n• Service issues\n• Account: {customer_type.title()}")
    else:
        resp.message(f"🤖 Hi {customer_name}! I didn't understand that. Try asking about 'wifi', 'hardware', or say 'help'. For urgent issues, use words like 'urgent' or 'escalate'.")
    
    return str(resp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

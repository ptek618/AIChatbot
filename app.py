from flask import Flask, request, jsonify
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

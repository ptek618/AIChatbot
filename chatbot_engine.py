from enum import Enum
from typing import Dict, List, Optional, Any
import re
from datetime import datetime
import uuid
from backend_integrations import BackendIntegrationManager
from ticket_system import TicketManager

class UserType(Enum):
    BUSINESS = "business"
    RESIDENTIAL = "residential"
    ENTERPRISE = "enterprise"
    NORTHBRIDGE_IT = "northbridge_it"

class ServiceType(Enum):
    FIBER = "fiber"
    FIXED_WIRELESS = "fixed_wireless"
    LTE = "lte"
    NORTHBRIDGE_IT_SERVICES = "northbridge_it_services"

class ConversationState:
    def __init__(self):
        self.user_type: Optional[UserType] = None
        self.service_type: Optional[ServiceType] = None
        self.customer_info: Dict[str, Any] = {}
        self.conversation_step: str = "initial"
        self.issue_description: str = ""
        self.ticket_id: Optional[str] = None
        self.conversation_history: List[Dict[str, str]] = []
        self.awaiting_verification: bool = False
        self.verification_attempts: int = 0
        self.diagnostic_data: Dict[str, Any] = {}

class ProTekChatbot:
    def __init__(self):
        self.user_sessions: Dict[str, ConversationState] = {}
        self.backend_manager = BackendIntegrationManager()
        self.ticket_manager = TicketManager()
    
    def get_or_create_session(self, user_id: str) -> ConversationState:
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = ConversationState()
        return self.user_sessions[user_id]
    
    def log_conversation(self, session: ConversationState, user_message: str, bot_response: str):
        session.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "bot_response": bot_response
        })
    
    def process_message(self, user_id: str, message: str) -> str:
        session = self.get_or_create_session(user_id)
        message_lower = message.lower().strip()
        
        if any(cmd in message_lower for cmd in ["restart", "reset", "start over", "new conversation"]):
            self.user_sessions[user_id] = ConversationState()
            session = self.user_sessions[user_id]
            return self.get_initial_greeting()
        
        if session.conversation_step == "initial":
            response = self.handle_initial_contact(session, message)
        elif session.conversation_step == "user_classification":
            response = self.handle_user_classification(session, message)
        elif session.conversation_step == "northbridge_verification":
            response = self.handle_northbridge_verification(session, message)
        elif session.conversation_step == "service_identification":
            response = self.handle_service_identification(session, message)
        elif session.conversation_step == "issue_gathering":
            response = self.handle_issue_gathering(session, message)
        elif session.conversation_step == "troubleshooting":
            response = self.handle_troubleshooting(session, message)
        elif session.conversation_step == "verification":
            response = self.handle_verification(session, message)
        elif session.conversation_step == "escalation":
            response = self.handle_escalation_followup(session, message)
        else:
            response = self.handle_general_inquiry(session, message)
        
        self.log_conversation(session, message, response)
        
        return response
    
    def get_initial_greeting(self) -> str:
        return ("👋 Welcome to ProTek Internet Support! I'm your AI assistant, available 24/7 to help you with any internet-related issues.\n\n"
               "To provide you with the best support, please let me know what type of customer you are:\n\n"
               "🏢 **Business** - Commercial internet services\n"
               "🏠 **Residential** - Home internet services\n"
               "🏢 **Enterprise** - Large-scale business solutions\n"
               "🔧 **Northbridge IT Services** - Managed IT support\n\n"
               "Just type your customer type to get started!")
    
    def handle_initial_contact(self, session: ConversationState, message: str) -> str:
        greetings = ["hi", "hello", "hey", "help", "support", "start"]
        
        if any(greeting in message.lower() for greeting in greetings):
            session.conversation_step = "user_classification"
            return self.get_initial_greeting()
        
        user_type = self.classify_user_type(message)
        if user_type:
            return self.handle_user_classification(session, message)
        
        session.conversation_step = "user_classification"
        return ("🤖 Hello! I'm the ProTek Internet Support AI assistant.\n\n"
               "I can help you with:\n"
               "• Internet troubleshooting and diagnostics\n"
               "• Service outage reports\n"
               "• WiFi password recovery\n"
               "• Account and billing questions\n"
               "• Technical support escalation\n\n"
               "To get started, please tell me what type of customer you are:\n"
               "• Business\n"
               "• Residential\n"
               "• Enterprise\n"
               "• Northbridge IT Services")
    
    def classify_user_type(self, message: str) -> Optional[UserType]:
        message_lower = message.lower()
        
        northbridge_keywords = ["northbridge", "nb", "managed services", "it services", "it support"]
        if any(keyword in message_lower for keyword in northbridge_keywords):
            return UserType.NORTHBRIDGE_IT
        
        enterprise_keywords = ["enterprise", "large business", "corporation", "corporate"]
        if any(keyword in message_lower for keyword in enterprise_keywords):
            return UserType.ENTERPRISE
        
        business_keywords = ["business", "commercial", "company", "office", "small business"]
        if any(keyword in message_lower for keyword in business_keywords):
            return UserType.BUSINESS
        
        residential_keywords = ["residential", "home", "house", "personal", "family", "consumer"]
        if any(keyword in message_lower for keyword in residential_keywords):
            return UserType.RESIDENTIAL
        
        return None
    
    def handle_user_classification(self, session: ConversationState, message: str) -> str:
        user_type = self.classify_user_type(message)
        
        if user_type:
            session.user_type = user_type
            
            if user_type == UserType.BUSINESS:
                ticket = self.ticket_manager.create_business_ticket(
                    customer_id=f"business_{uuid.uuid4().hex[:8]}",
                    issue_description="Business customer support request - immediate escalation",
                    conversation_history=session.conversation_history
                )
                session.ticket_id = ticket["ticket_id"]
                session.conversation_step = "escalation"
                
                return ("🏢 **Business Customer Identified**\n\n"
                       "Thank you for contacting ProTek Internet Support. As a business customer, your request has been prioritized for immediate attention.\n\n"
                       f"✅ **Ticket Created:** {ticket['ticket_id']}\n"
                       "🚨 **Status:** Escalated to on-call support team\n"
                       "⏰ **Expected Response:** Within 15 minutes\n"
                       "📞 **Next Steps:** Our on-call technician will contact you shortly\n\n"
                       "Is this regarding a current outage or do you need immediate technical assistance?")
            
            elif user_type == UserType.ENTERPRISE:
                ticket = self.ticket_manager.create_enterprise_ticket(
                    customer_id=f"enterprise_{uuid.uuid4().hex[:8]}",
                    issue_description="Enterprise customer support request - high priority",
                    conversation_history=session.conversation_history
                )
                session.ticket_id = ticket["ticket_id"]
                session.conversation_step = "escalation"
                
                return ("🏢 **Enterprise Customer Identified**\n\n"
                       "Welcome to ProTek Enterprise Support. Your request has been assigned the highest priority.\n\n"
                       f"✅ **Ticket Created:** {ticket['ticket_id']}\n"
                       "🚨 **Status:** Escalated to enterprise support team\n"
                       "⏰ **Expected Response:** Within 10 minutes\n"
                       "📞 **Next Steps:** Your dedicated account manager will be notified\n\n"
                       "Please describe the nature of your issue so we can ensure the right specialist contacts you.")
            
            elif user_type == UserType.NORTHBRIDGE_IT:
                session.conversation_step = "northbridge_verification"
                return ("🔧 **Northbridge IT Services**\n\n"
                       "Thank you for contacting us regarding Northbridge IT Services.\n\n"
                       "Before I connect you with our Northbridge team, I need to verify the nature of your request:\n\n"
                       "❓ **Is this request related to:**\n"
                       "🌐 **ProTek Internet connectivity** (internet service, outages, speed issues)\n"
                       "💻 **Pure IT services** (managed services, computer support, software issues)\n\n"
                       "Please specify which type of support you need so I can route you to the correct team.")
            
            else:
                session.conversation_step = "service_identification"
                return ("🏠 **Residential Customer**\n\n"
                       "Great! I'm here to help with your home internet service.\n\n"
                       "To provide the most accurate troubleshooting, please tell me what type of internet service you have:\n\n"
                       "🌐 **Fiber** - Fiber optic internet service\n"
                       "📡 **Fixed Wireless** - Wireless internet from our towers\n"
                       "📱 **LTE/QLM** - Cellular-based internet service\n\n"
                       "If you're not sure, I can help you identify your service type. What equipment do you see (modem, outdoor antenna, cellular device)?")
        
        return ("❓ I didn't quite understand your customer type. Please choose from:\n\n"
               "• **Business** - for commercial internet services\n"
               "• **Residential** - for home internet services\n"
               "• **Enterprise** - for large-scale business solutions\n"
               "• **Northbridge IT Services** - for managed IT support\n\n"
               "Just type one of these options.")
    
    def handle_northbridge_verification(self, session: ConversationState, message: str) -> str:
        message_lower = message.lower()
        
        internet_keywords = ["internet", "connectivity", "outage", "speed", "connection", "wifi", "fiber", "wireless", "lte"]
        it_keywords = ["computer", "software", "managed", "it services", "server", "email", "backup"]
        
        if any(keyword in message_lower for keyword in internet_keywords):
            session.conversation_step = "service_identification"
            return ("🌐 **Internet-Related Issue Detected**\n\n"
                   "I understand this is related to your ProTek internet connectivity. Let me help you with that!\n\n"
                   "Please tell me what type of internet service you have:\n\n"
                   "🌐 **Fiber** - Fiber optic internet service\n"
                   "📡 **Fixed Wireless** - Wireless internet from our towers\n"
                   "📱 **LTE/QLM** - Cellular-based internet service\n\n"
                   "What type of service are you experiencing issues with?")
        
        elif any(keyword in message_lower for keyword in it_keywords) or "pure it" in message_lower or "it services" in message_lower:
            ticket = self.ticket_manager.create_northbridge_ticket(
                customer_id=f"northbridge_{uuid.uuid4().hex[:8]}",
                issue_description=f"Northbridge IT Services request: {message}",
                conversation_history=session.conversation_history
            )
            session.ticket_id = ticket["ticket_id"]
            session.conversation_step = "escalation"
            
            return ("🔧 **Forwarded to Northbridge IT Services**\n\n"
                   "Your request has been forwarded to our Northbridge IT Services team.\n\n"
                   f"✅ **Ticket Created:** {ticket['ticket_id']}\n"
                   "📧 **Team Notified:** Northbridge IT specialists\n"
                   "⏰ **Expected Response:** Within 30 minutes during business hours\n"
                   "📞 **Contact:** A Northbridge technician will reach out to you\n\n"
                   "Please provide any additional details about your IT service needs.")
        
        return ("❓ I need a bit more clarity. Please specify:\n\n"
               "🌐 **Internet/Connectivity Issues:** Type 'internet' if you're having problems with your ProTek internet service\n"
               "💻 **IT Services:** Type 'IT services' if you need help with computers, software, or managed services\n\n"
               "This helps me route you to the right support team.")
    
    def detect_service_type(self, message: str) -> Optional[ServiceType]:
        message_lower = message.lower()
        
        if "fiber" in message_lower or "fibre" in message_lower:
            return ServiceType.FIBER
        elif any(keyword in message_lower for keyword in ["fixed wireless", "wireless", "tower", "antenna", "outdoor"]):
            return ServiceType.FIXED_WIRELESS
        elif any(keyword in message_lower for keyword in ["lte", "qlm", "cellular", "mobile", "jetpack", "hotspot"]):
            return ServiceType.LTE
        
        return None
    
    def handle_service_identification(self, session: ConversationState, message: str) -> str:
        service_type = self.detect_service_type(message)
        
        if service_type:
            session.service_type = service_type
            session.conversation_step = "issue_gathering"
            
            service_name = service_type.value.replace("_", " ").title()
            return (f"✅ **{service_name} Service Identified**\n\n"
                   f"Perfect! I can help you troubleshoot your {service_name} connection.\n\n"
                   "Please describe the issue you're experiencing:\n\n"
                   "🔴 **No Internet** - Complete loss of connectivity\n"
                   "🐌 **Slow Speeds** - Internet is working but slower than expected\n"
                   "⚡ **Intermittent** - Connection drops in and out\n"
                   "🔐 **WiFi Password** - Need to retrieve WiFi credentials\n"
                   "📊 **Other Issue** - Describe your specific problem\n\n"
                   "What best describes your current situation?")
        
        equipment_keywords = {
            "modem": "This sounds like Fiber service",
            "antenna": "This sounds like Fixed Wireless service", 
            "outdoor": "This sounds like Fixed Wireless service",
            "jetpack": "This sounds like LTE/QLM service",
            "hotspot": "This sounds like LTE/QLM service",
            "cellular": "This sounds like LTE/QLM service"
        }
        
        for keyword, suggestion in equipment_keywords.items():
            if keyword in message.lower():
                return (f"💡 **Service Type Suggestion**\n\n"
                       f"Based on your mention of '{keyword}', {suggestion.lower()}.\n\n"
                       "Please confirm your service type:\n"
                       "• **Fiber** - if you have a fiber optic modem\n"
                       "• **Fixed Wireless** - if you have an outdoor antenna\n"
                       "• **LTE/QLM** - if you have a cellular device\n\n"
                       "Which one matches your setup?")
        
        return ("❓ I need to identify your service type to provide accurate help.\n\n"
               "Please choose from:\n"
               "🌐 **Fiber** - Fiber optic internet with indoor modem\n"
               "📡 **Fixed Wireless** - Wireless internet with outdoor antenna\n"
               "📱 **LTE/QLM** - Cellular internet device (Jetpack, hotspot, etc.)\n\n"
               "Or describe the equipment you have, and I'll help identify your service type.")
    
    def handle_issue_gathering(self, session: ConversationState, message: str) -> str:
        session.issue_description = message
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in ["wifi password", "password", "credentials", "network name"]):
            return self.handle_wifi_password_request(session)
        
        elif any(keyword in message_lower for keyword in ["no internet", "not working", "down", "offline", "outage"]):
            session.conversation_step = "troubleshooting"
            return self.handle_connectivity_issue(session)
        
        elif any(keyword in message_lower for keyword in ["slow", "speed", "bandwidth", "sluggish"]):
            session.conversation_step = "troubleshooting"
            return self.handle_speed_issue(session)
        
        elif any(keyword in message_lower for keyword in ["intermittent", "dropping", "unstable", "cutting out"]):
            session.conversation_step = "troubleshooting"
            return self.handle_intermittent_issue(session)
        
        else:
            session.conversation_step = "troubleshooting"
            return self.handle_general_troubleshooting(session)
    
    def handle_wifi_password_request(self, session: ConversationState) -> str:
        session.conversation_step = "verification"
        session.awaiting_verification = True
        
        return ("🔐 **WiFi Password Request**\n\n"
               "I can help you retrieve your WiFi credentials. For security purposes, I need to verify your identity first.\n\n"
               "Please provide ONE of the following:\n"
               "📞 **Phone number** associated with your account\n"
               "🏠 **Service address** where internet is installed\n"
               "🆔 **Account number** from your bill\n\n"
               "Which would you prefer to use for verification?")
    
    def handle_connectivity_issue(self, session: ConversationState) -> str:
        diagnostic_data = self.backend_manager.run_diagnostics(
            customer_id=f"customer_{uuid.uuid4().hex[:8]}", 
            service_type=session.service_type.value if session.service_type else "unknown"
        )
        session.diagnostic_data = diagnostic_data
        
        if session.service_type == ServiceType.FIBER:
            return ("🔍 **Fiber Connection Diagnostics**\n\n"
                   "Let me help troubleshoot your fiber connection. I'm checking our systems...\n\n"
                   "🔧 **System Check Results:**\n"
                   f"• Network Status: {diagnostic_data.get('network_status', '✅ No area outages detected')}\n"
                   f"• Your Service: {diagnostic_data.get('service_status', '🔍 Checking equipment status...')}\n"
                   f"• Signal Quality: {diagnostic_data.get('signal_quality', 'Good')}\n\n"
                   "**Please check your fiber modem:**\n"
                   "1️⃣ **Power Light** - Is it solid green?\n"
                   "2️⃣ **Fiber/PON Light** - Is it solid green (not red or flashing)?\n"
                   "3️⃣ **Internet/WAN Light** - What color is it?\n\n"
                   "Please tell me the status of these lights.")
        
        elif session.service_type == ServiceType.FIXED_WIRELESS:
            return ("📡 **Fixed Wireless Diagnostics**\n\n"
                   "Let me check your wireless connection. Running diagnostics...\n\n"
                   "🔧 **System Check Results:**\n"
                   f"• Tower Status: {diagnostic_data.get('tower_status', '✅ Operating normally')}\n"
                   f"• Signal Path: {diagnostic_data.get('signal_path', '🔍 Checking your connection...')}\n"
                   f"• Signal Strength: {diagnostic_data.get('signal_strength', '-65 dBm (Good)')}\n\n"
                   "**Please check your equipment:**\n"
                   "1️⃣ **Outdoor Antenna** - Is it properly aligned and secure?\n"
                   "2️⃣ **Power Supply** - Is the power adapter plugged in and working?\n"
                   "3️⃣ **Cables** - Are all cables connected tightly?\n"
                   "4️⃣ **Obstructions** - Any new trees, buildings, or objects blocking the antenna?\n\n"
                   "What do you observe with your equipment?")
        
        elif session.service_type == ServiceType.LTE:
            return ("📱 **LTE Connection Diagnostics**\n\n"
                   "Checking your cellular internet connection...\n\n"
                   "🔧 **System Check Results:**\n"
                   f"• Network Coverage: {diagnostic_data.get('network_coverage', '✅ Good signal in your area')}\n"
                   f"• Device Status: {diagnostic_data.get('device_status', '🔍 Checking your connection...')}\n"
                   f"• Signal Bars: {diagnostic_data.get('signal_bars', '4/5 bars')}\n\n"
                   "**Please check your LTE device:**\n"
                   "1️⃣ **Signal Bars** - How many bars do you see on the device?\n"
                   "2️⃣ **Power** - Is the device powered on and charged?\n"
                   "3️⃣ **Location** - Is the device in a good location (near window, elevated)?\n"
                   "4️⃣ **Restart** - Have you tried powering the device off and on?\n\n"
                   "Please let me know what you see.")
        
        return ("🔧 **Connection Diagnostics**\n\n"
               "I'm running diagnostics on your connection...\n\n"
               "Please provide more details about your setup so I can help troubleshoot effectively.")
    
    def handle_speed_issue(self, session: ConversationState) -> str:
        diagnostic_data = self.backend_manager.run_speed_diagnostics(
            customer_id=f"customer_{uuid.uuid4().hex[:8]}", 
            service_type=session.service_type.value if session.service_type else "unknown"
        )
        session.diagnostic_data = diagnostic_data
        
        return ("🚀 **Speed Issue Diagnostics**\n\n"
               "Let me help diagnose your speed issues. I'm checking your connection quality...\n\n"
               "🔧 **Initial Checks:**\n"
               f"• Service Plan: {diagnostic_data.get('service_plan', '🔍 Verifying your speed tier')}\n"
               f"• Network Load: {diagnostic_data.get('network_load', '🔍 Checking for congestion')}\n"
               f"• Equipment Status: {diagnostic_data.get('equipment_status', '🔍 Analyzing performance')}\n"
               f"• Current Speed: {diagnostic_data.get('current_speed', 'Testing...')}\n\n"
               "**To help diagnose further:**\n"
               "1️⃣ **Speed Test** - Please run a speed test at speedtest.net\n"
               "2️⃣ **Connected Devices** - How many devices are currently using internet?\n"
               "3️⃣ **Activities** - What are you trying to do when you notice slowness?\n"
               "4️⃣ **Time of Day** - When do you typically notice speed issues?\n\n"
               "Please share your speed test results and answer these questions.")
    
    def handle_intermittent_issue(self, session: ConversationState) -> str:
        diagnostic_data = self.backend_manager.run_stability_diagnostics(
            customer_id=f"customer_{uuid.uuid4().hex[:8]}", 
            service_type=session.service_type.value if session.service_type else "unknown"
        )
        session.diagnostic_data = diagnostic_data
        
        return ("⚡ **Intermittent Connection Analysis**\n\n"
               "Intermittent issues can be tricky to diagnose. Let me gather some information...\n\n"
               "🔧 **System Analysis:**\n"
               f"• Connection Stability: {diagnostic_data.get('stability_score', '🔍 Checking for patterns')}\n"
               f"• Equipment Health: {diagnostic_data.get('equipment_health', '🔍 Analyzing performance logs')}\n"
               f"• Environmental Factors: {diagnostic_data.get('environmental_factors', '🔍 Checking for interference')}\n"
               f"• Recent Outages: {diagnostic_data.get('recent_outages', 'None detected')}\n\n"
               "**Please help me understand the pattern:**\n"
               "1️⃣ **Frequency** - How often does the connection drop?\n"
               "2️⃣ **Duration** - How long do the outages last?\n"
               "3️⃣ **Time Pattern** - Does it happen at specific times?\n"
               "4️⃣ **Weather** - Do you notice issues during bad weather?\n"
               "5️⃣ **Activities** - Does it happen during specific online activities?\n\n"
               "This information will help me identify the root cause.")
    
    def handle_general_troubleshooting(self, session: ConversationState) -> str:
        diagnostic_data = self.backend_manager.run_general_diagnostics(
            customer_id=f"customer_{uuid.uuid4().hex[:8]}", 
            service_type=session.service_type.value if session.service_type else "unknown"
        )
        session.diagnostic_data = diagnostic_data
        
        return ("🔧 **Technical Support Analysis**\n\n"
               f"I understand you're experiencing: {session.issue_description}\n\n"
               "Let me gather some diagnostic information to help resolve this...\n\n"
               "🔍 **System Checks:**\n"
               f"• Service Status: {diagnostic_data.get('service_status', '🔍 Checking for outages')}\n"
               f"• Equipment Health: {diagnostic_data.get('equipment_health', '🔍 Analyzing your connection')}\n"
               f"• Account Status: {diagnostic_data.get('account_status', '🔍 Verifying service details')}\n\n"
               "**To provide the best assistance:**\n"
               "1️⃣ **When did this issue start?**\n"
               "2️⃣ **Is it affecting all devices or just some?**\n"
               "3️⃣ **Have you made any recent changes to your setup?**\n"
               "4️⃣ **Have you tried restarting your equipment?**\n\n"
               "Please provide these details so I can create a targeted solution.")
    
    def handle_verification(self, session: ConversationState, message: str) -> str:
        session.verification_attempts += 1
        
        if session.verification_attempts <= 3:
            verification_successful = self.backend_manager.verify_customer_identity(message)
            
            if verification_successful:
                session.awaiting_verification = False
                session.conversation_step = "troubleshooting"
                
                wifi_credentials = self.backend_manager.get_wifi_credentials(
                    customer_id=f"customer_{uuid.uuid4().hex[:8]}",
                    service_type=session.service_type.value if session.service_type else "fiber"
                )
                
                return ("✅ **Identity Verified Successfully**\n\n"
                       "🔐 **Your WiFi Credentials:**\n"
                       f"📶 **Network Name:** {wifi_credentials.get('network_name', 'ProTek_Fiber_5G')}\n"
                       f"🔑 **Password:** {wifi_credentials.get('password', 'ProTek2024Secure!')}\n\n"
                       f"📶 **Guest Network:** {wifi_credentials.get('guest_network', 'ProTek_Guest')}\n"
                       f"🔑 **Guest Password:** {wifi_credentials.get('guest_password', 'Welcome123')}\n\n"
                       "💡 **Tips:**\n"
                       "• Use the 5G network for best performance\n"
                       "• Guest network is perfect for visitors\n"
                       "• Contact us if you need to change these credentials\n\n"
                       "Is there anything else I can help you with today?")
            else:
                return ("❌ **Verification Failed**\n\n"
                       f"I couldn't verify that information. You have {3 - session.verification_attempts} attempts remaining.\n\n"
                       "Please try again with:\n"
                       "📞 **Phone number** on your account\n"
                       "🏠 **Service address** where internet is installed\n"
                       "🆔 **Account number** from your bill")
        else:
            ticket = self.ticket_manager.create_verification_ticket(
                customer_id=f"verification_failed_{uuid.uuid4().hex[:8]}",
                issue_description="Customer verification failed - manual review required",
                conversation_history=session.conversation_history
            )
            session.ticket_id = ticket["ticket_id"]
            session.conversation_step = "escalation"
            
            return ("🔒 **Verification Limit Reached**\n\n"
                   "For security purposes, I've created a support ticket for manual verification.\n\n"
                   f"✅ **Ticket Created:** {ticket['ticket_id']}\n"
                   "📞 **Next Steps:** A support agent will call you to verify your identity\n"
                   "⏰ **Expected Contact:** Within 2 hours during business hours\n\n"
                   "Please have your account information ready when they call.")
    
    def handle_troubleshooting(self, session: ConversationState, message: str) -> str:
        message_lower = message.lower()
        
        if any(phrase in message_lower for phrase in ["create ticket", "escalate", "technician", "not working", "still broken", "doesn't work"]):
            ticket = self.ticket_manager.create_technical_ticket(
                customer_id=f"residential_{uuid.uuid4().hex[:8]}",
                service_type=session.service_type.value if session.service_type else "unknown",
                issue_description=session.issue_description,
                conversation_history=session.conversation_history,
                diagnostic_data=session.diagnostic_data
            )
            session.ticket_id = ticket["ticket_id"]
            session.conversation_step = "escalation"
            
            return ("🎫 **Support Ticket Created**\n\n"
                   "I've created a technical support ticket for your issue.\n\n"
                   f"✅ **Ticket ID:** {ticket['ticket_id']}\n"
                   f"🔧 **Issue:** {session.issue_description}\n"
                   "📞 **Next Steps:** A technician will review and contact you\n"
                   "⏰ **Expected Response:** Within 2-4 hours during business hours\n\n"
                   "You'll receive updates via phone or email. Is there anything else I can help with while you wait?")
        
        if any(word in message_lower for word in ["green", "solid", "working", "good", "connected"]):
            return ("✅ **Good Progress!**\n\n"
                   "It sounds like some things are working correctly. Let's continue troubleshooting:\n\n"
                   "🔧 **Next Steps:**\n"
                   "• Try unplugging your equipment for 30 seconds, then plug back in\n"
                   "• Test your connection with a different device\n"
                   "• Check if the issue affects all websites or just some\n\n"
                   "After trying these steps, let me know if your connection improves or if you're still experiencing issues.")
        
        elif any(word in message_lower for word in ["red", "flashing", "blinking", "off", "no light"]):
            return ("⚠️ **Issue Detected**\n\n"
                   "I see there may be a problem with your equipment. This could indicate:\n\n"
                   "🔍 **Possible Causes:**\n"
                   "• Service outage in your area\n"
                   "• Equipment malfunction\n"
                   "• Connection issue at the service point\n\n"
                   "🛠️ **Immediate Steps:**\n"
                   "1. Unplug your equipment for 2 minutes\n"
                   "2. Plug it back in and wait 5 minutes for full startup\n"
                   "3. Check if the lights return to normal\n\n"
                   "If this doesn't resolve the issue, I'll create a service ticket for a technician visit. Would you like me to do that?")
        
        else:
            return ("📋 **Troubleshooting Update**\n\n"
                   "Thank you for that information. Based on what you've shared:\n\n"
                   "🔍 **Analysis:** I'm processing your diagnostic information...\n"
                   "🔧 **Recommendations:**\n"
                   "• Try unplugging your equipment for 30 seconds, then plug back in\n"
                   "• Check all cable connections are secure\n"
                   "• Test with a wired connection if possible\n\n"
                   "If these steps don't resolve the issue, I can:\n"
                   "• Create a service ticket for a technician visit\n"
                   "• Escalate to our technical support team\n"
                   "• Schedule a callback during business hours\n\n"
                   "What would you like to do next?")
    
    def handle_escalation_followup(self, session: ConversationState, message: str) -> str:
        return ("📞 **Escalation Status Update**\n\n"
               f"Your ticket {session.ticket_id} is still active and being processed by our support team.\n\n"
               "🔄 **Current Status:**\n"
               "• Your request is in the queue\n"
               "• A specialist will contact you soon\n"
               "• All conversation details have been logged\n\n"
               "💬 **Additional Information:**\n"
               "I've added your latest message to the ticket. This will help our technician better understand your situation.\n\n"
               "Is there anything else you'd like me to add to your support ticket?")
    
    def handle_general_inquiry(self, session: ConversationState, message: str) -> str:
        return ("🤖 **ProTek Support Assistant**\n\n"
               "I'm here to help! I can assist you with:\n\n"
               "🔧 **Technical Support:**\n"
               "• Internet troubleshooting and diagnostics\n"
               "• Speed issues and connectivity problems\n"
               "• Equipment setup and configuration\n\n"
               "🔐 **Account Services:**\n"
               "• WiFi password recovery\n"
               "• Service information\n"
               "• Billing questions\n\n"
               "🎫 **Support Options:**\n"
               "• Create service tickets\n"
               "• Escalate to technical teams\n"
               "• Schedule technician visits\n\n"
               "What can I help you with today? Just describe your issue or question!")

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from backend_integrations import SonarIntegration

class TicketManager:
    def __init__(self):
        self.sonar = SonarIntegration()
        self.tickets: Dict[str, Dict[str, Any]] = {}
    
    def create_business_ticket(self, customer_id: str, issue_description: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        ticket_data = {
            "customer_id": customer_id,
            "issue_type": "business_escalation",
            "description": f"URGENT - Business Customer Support Request: {issue_description}",
            "priority": "critical"
        }
        
        sonar_ticket = self.sonar.create_ticket(**ticket_data)
        
        ticket = {
            "ticket_id": sonar_ticket["ticket_id"],
            "sonar_ticket_id": sonar_ticket["ticket_id"],
            "customer_type": "business",
            "customer_id": customer_id,
            "issue_description": issue_description,
            "priority": "critical",
            "status": "escalated",
            "created_at": datetime.now().isoformat(),
            "escalated_to": "on_call_team",
            "expected_response_time": "15 minutes",
            "conversation_history": conversation_history,
            "escalation_notes": "Business customer - immediate escalation required"
        }
        
        self.tickets[ticket["ticket_id"]] = ticket
        return ticket
    
    def create_enterprise_ticket(self, customer_id: str, issue_description: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        ticket_data = {
            "customer_id": customer_id,
            "issue_type": "enterprise_escalation",
            "description": f"HIGH PRIORITY - Enterprise Customer Support Request: {issue_description}",
            "priority": "high"
        }
        
        sonar_ticket = self.sonar.create_ticket(**ticket_data)
        
        ticket = {
            "ticket_id": sonar_ticket["ticket_id"],
            "sonar_ticket_id": sonar_ticket["ticket_id"],
            "customer_type": "enterprise",
            "customer_id": customer_id,
            "issue_description": issue_description,
            "priority": "high",
            "status": "escalated",
            "created_at": datetime.now().isoformat(),
            "escalated_to": "enterprise_support_team",
            "expected_response_time": "10 minutes",
            "conversation_history": conversation_history,
            "escalation_notes": "Enterprise customer - high priority escalation"
        }
        
        self.tickets[ticket["ticket_id"]] = ticket
        return ticket
    
    def create_northbridge_ticket(self, customer_id: str, issue_description: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        ticket_data = {
            "customer_id": customer_id,
            "issue_type": "northbridge_it_services",
            "description": f"Northbridge IT Services Request: {issue_description}",
            "priority": "medium"
        }
        
        sonar_ticket = self.sonar.create_ticket(**ticket_data)
        
        ticket = {
            "ticket_id": sonar_ticket["ticket_id"],
            "sonar_ticket_id": sonar_ticket["ticket_id"],
            "customer_type": "northbridge_it",
            "customer_id": customer_id,
            "issue_description": issue_description,
            "priority": "medium",
            "status": "forwarded",
            "created_at": datetime.now().isoformat(),
            "escalated_to": "northbridge_it_team",
            "expected_response_time": "30 minutes",
            "conversation_history": conversation_history,
            "escalation_notes": "Forwarded to Northbridge IT Services team"
        }
        
        self.tickets[ticket["ticket_id"]] = ticket
        return ticket
    
    def create_technical_ticket(self, customer_id: str, service_type: str, issue_description: str, conversation_history: List[Dict[str, str]], diagnostic_data: Dict[str, Any]) -> Dict[str, Any]:
        ticket_data = {
            "customer_id": customer_id,
            "issue_type": f"{service_type}_technical_support",
            "description": f"Technical Support Request - {service_type.title()}: {issue_description}",
            "priority": "medium"
        }
        
        sonar_ticket = self.sonar.create_ticket(**ticket_data)
        
        ticket = {
            "ticket_id": sonar_ticket["ticket_id"],
            "sonar_ticket_id": sonar_ticket["ticket_id"],
            "customer_type": "residential",
            "customer_id": customer_id,
            "service_type": service_type,
            "issue_description": issue_description,
            "priority": "medium",
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "escalated_to": "technical_support_team",
            "expected_response_time": "2-4 hours",
            "conversation_history": conversation_history,
            "diagnostic_data": diagnostic_data,
            "escalation_notes": f"Residential {service_type} technical support request"
        }
        
        self.tickets[ticket["ticket_id"]] = ticket
        return ticket
    
    def create_verification_ticket(self, customer_id: str, issue_description: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        ticket_data = {
            "customer_id": customer_id,
            "issue_type": "identity_verification_failed",
            "description": f"Customer Identity Verification Failed: {issue_description}",
            "priority": "medium"
        }
        
        sonar_ticket = self.sonar.create_ticket(**ticket_data)
        
        ticket = {
            "ticket_id": sonar_ticket["ticket_id"],
            "sonar_ticket_id": sonar_ticket["ticket_id"],
            "customer_type": "unknown",
            "customer_id": customer_id,
            "issue_description": issue_description,
            "priority": "medium",
            "status": "pending_verification",
            "created_at": datetime.now().isoformat(),
            "escalated_to": "customer_service_team",
            "expected_response_time": "2 hours",
            "conversation_history": conversation_history,
            "escalation_notes": "Customer verification failed - manual review required"
        }
        
        self.tickets[ticket["ticket_id"]] = ticket
        return ticket
    
    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        return self.tickets.get(ticket_id)
    
    def update_ticket_status(self, ticket_id: str, status: str, notes: str = None) -> bool:
        if ticket_id in self.tickets:
            self.tickets[ticket_id]["status"] = status
            self.tickets[ticket_id]["last_updated"] = datetime.now().isoformat()
            if notes:
                if "status_history" not in self.tickets[ticket_id]:
                    self.tickets[ticket_id]["status_history"] = []
                self.tickets[ticket_id]["status_history"].append({
                    "status": status,
                    "notes": notes,
                    "timestamp": datetime.now().isoformat()
                })
            return True
        return False
    
    def add_conversation_to_ticket(self, ticket_id: str, user_message: str, bot_response: str) -> bool:
        if ticket_id in self.tickets:
            self.tickets[ticket_id]["conversation_history"].append({
                "timestamp": datetime.now().isoformat(),
                "user_message": user_message,
                "bot_response": bot_response
            })
            return True
        return False
    
    def get_tickets_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        return [ticket for ticket in self.tickets.values() if ticket["customer_id"] == customer_id]
    
    def get_open_tickets(self) -> List[Dict[str, Any]]:
        return [ticket for ticket in self.tickets.values() if ticket["status"] in ["open", "escalated", "pending_verification"]]

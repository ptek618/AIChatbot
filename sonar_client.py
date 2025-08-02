import requests
import os
from typing import Dict, Any, Optional
import logging

class SonarClient:
    def __init__(self):
        self.api_url = os.getenv('SONAR_API_URL')
        self.api_token = os.getenv('SONAR_API_TOKEN')
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def create_internal_ticket(self, 
                             subject: str, 
                             description: str, 
                             customer_data: Optional[Dict[str, Any]] = None,
                             priority: str = 'MEDIUM',
                             status: str = 'OPEN') -> Optional[Dict[str, Any]]:
        """Create an internal ticket in Sonar"""
        
        mutation = """
        mutation CreateInternalTicket($input: CreateInternalTicketMutationInput!) {
            createInternalTicket(input: $input) {
                id
                subject
                description
                status
                priority
                created_at
            }
        }
        """
        
        variables = {
            "input": {
                "subject": subject,
                "description": description,
                "status": status,
                "priority": priority,
                "user_id": 65  # Assign to Chat_API user
            }
        }
        
        if customer_data and customer_data.get('account_id'):
            variables["input"]["ticketable_type"] = "ACCOUNT"
            variables["input"]["ticketable_id"] = int(customer_data['account_id'])
        
        try:
            response = requests.post(
                self.api_url,
                json={"query": mutation, "variables": variables},
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if 'errors' in result:
                logging.error(f"Sonar API errors: {result['errors']}")
                return None
            
            return result.get('data', {}).get('createInternalTicket')
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to create Sonar ticket: {e}")
            return None

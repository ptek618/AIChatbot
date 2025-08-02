import json
import os
from typing import Dict, Optional, Any

class CustomerDatabase:
    def __init__(self, data_file='customers.json'):
        self.data_file = data_file
        self.customers = self._load_customers()
    
    def _load_customers(self) -> Dict[str, Any]:
        """Load customer data from JSON file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {}
    
    def authenticate_customer(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Authenticate customer by phone number"""
        normalized_phone = ''.join(filter(str.isdigit, phone_number))[-10:]
        return self.customers.get(normalized_phone)
    
    def get_customer_type(self, customer_data: Dict[str, Any]) -> str:
        """Get customer type (business, residential, etc.)"""
        return customer_data.get('type', 'residential')
    
    def get_customer_hardware(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get customer hardware information"""
        return customer_data.get('hardware', {})
    
    def get_wifi_password(self, customer_data: Dict[str, Any]) -> Optional[str]:
        """Get wifi password for authorized customers"""
        if customer_data.get('wifi_access_authorized', False):
            return customer_data.get('wifi_password')
        return None
    
    def add_sample_data(self):
        """Add sample customer data for testing"""
        self.customers = {
            "5551234567": {
                "name": "John Doe",
                "type": "residential",
                "account_id": "12345",
                "wifi_access_authorized": True,
                "wifi_password": "MySecureWifi123",
                "hardware": {
                    "modem": "Netgear CM1000",
                    "router": "ASUS AX6000"
                }
            },
            "5559876543": {
                "name": "ABC Business Corp",
                "type": "business",
                "account_id": "67890",
                "wifi_access_authorized": True,
                "wifi_password": "BusinessWifi456",
                "hardware": {
                    "modem": "Motorola MB8600",
                    "router": "Ubiquiti Dream Machine"
                }
            }
        }
        with open(self.data_file, 'w') as f:
            json.dump(self.customers, f, indent=2)

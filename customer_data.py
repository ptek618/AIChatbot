import requests
import os
from typing import Dict, Any, Optional
import logging
from dotenv import load_dotenv

class CustomerDatabase:
    def __init__(self):
        load_dotenv()
        self.api_url = os.getenv('SONAR_API_URL')
        self.api_token = os.getenv('SONAR_API_TOKEN')
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        self._cache = {}
    
    def _normalize_phone_number(self, phone_number: str) -> str:
        """Normalize phone number by removing non-digits and country codes"""
        digits_only = ''.join(filter(str.isdigit, phone_number))
        return digits_only[-10:] if len(digits_only) >= 10 else digits_only
    
    def _query_sonar(self, query: str, variables: Dict = None) -> Optional[Dict]:
        """Execute GraphQL query against Sonar API"""
        try:
            response = requests.post(
                self.api_url,
                json={'query': query, 'variables': variables or {}},
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if 'errors' in result:
                logging.error(f"Sonar GraphQL errors: {result['errors']}")
                return None
            
            return result.get('data')
        except Exception as e:
            logging.error(f"Sonar API query failed: {e}")
            return None
    
    def authenticate_customer(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Authenticate customer by phone number lookup in Sonar"""
        normalized_phone = self._normalize_phone_number(phone_number)
        
        if normalized_phone in self._cache:
            return self._cache[normalized_phone]
        
        query = '''
        query FindCustomerByPhone($phoneNumber: String!) {
          phone_numbers(
            search: {
              string_fields: [{
                attribute: "number"
                search_value: $phoneNumber
                match: true
                partial_matching: true
              }]
            }
            paginator: {page: 1, records_per_page: 5}
          ) {
            entities {
              id
              number
              number_formatted
              contact {
                id
                name
                role
                email_address
                contactable_id
                contactable_type
                contactable {
                  ... on Account {
                    id
                    name
                    account_type {
                      id
                      name
                    }
                    notes {
                      entities {
                        id
                        message
                        priority
                        created_at
                      }
                    }
                    custom_field_data {
                      entities {
                        id
                        value
                        custom_field {
                          id
                          name
                          type
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        '''
        
        variables = {"phoneNumber": normalized_phone}
        data = self._query_sonar(query, variables)
        
        if not data or not data.get('phone_numbers', {}).get('entities'):
            logging.info(f"No customer found for phone number: {phone_number}")
            return None
        
        phone_entity = data['phone_numbers']['entities'][0]
        contact = phone_entity.get('contact')
        
        if not contact or contact.get('contactable_type') != 'Account':
            logging.info(f"Phone number {phone_number} not linked to an account")
            return None
        
        account = contact.get('contactable')
        if not account:
            logging.info(f"No account data found for phone number: {phone_number}")
            return None
        
        customer_data = {
            'phone_number': phone_number,
            'normalized_phone': normalized_phone,
            'account_id': account.get('id'),
            'name': account.get('name', 'Unknown Customer'),
            'contact_name': contact.get('name'),
            'contact_role': contact.get('role'),
            'contact_email': contact.get('email_address'),
            'type': self._determine_customer_type(account),
            'notes': self._extract_notes(account.get('notes', {}).get('entities', [])),
            'custom_fields': self._extract_custom_fields(account.get('custom_field_data', {}).get('entities', [])),
            'wifi_access_authorized': self._check_wifi_authorization(account),
            'wifi_password': self._extract_wifi_password(account),
            'hardware': self._extract_hardware_info(account)
        }
        
        self._cache[normalized_phone] = customer_data
        return customer_data
    
    def _determine_customer_type(self, account: Dict) -> str:
        """Determine customer type from account data"""
        account_type = account.get('account_type', {})
        type_name = account_type.get('name', '').lower()
        
        if 'business' in type_name or 'commercial' in type_name:
            return 'business'
        elif 'residential' in type_name or 'home' in type_name:
            return 'residential'
        else:
            return 'residential'
    
    def _extract_notes(self, notes_entities: list) -> str:
        """Extract and combine notes from account"""
        if not notes_entities:
            return ""
        
        sorted_notes = sorted(notes_entities, key=lambda x: x.get('created_at', ''), reverse=True)
        return '\n'.join([note.get('message', '') for note in sorted_notes if note.get('message')])
    
    def _extract_custom_fields(self, custom_field_entities: list) -> Dict[str, Any]:
        """Extract custom fields into a dictionary"""
        custom_fields = {}
        for field_entity in custom_field_entities:
            field_info = field_entity.get('custom_field', {})
            field_name = field_info.get('name')
            field_value = field_entity.get('value')
            if field_name and field_value:
                custom_fields[field_name.lower()] = field_value
        return custom_fields
    
    def _check_wifi_authorization(self, account: Dict) -> bool:
        """Check if customer is authorized to receive WiFi passwords"""
        custom_fields = self._extract_custom_fields(account.get('custom_field_data', {}).get('entities', []))
        
        wifi_auth_fields = ['wifi_access', 'wifi_authorized', 'password_access', 'tech_support_access']
        for field_name in wifi_auth_fields:
            if field_name in custom_fields:
                value = str(custom_fields[field_name]).lower()
                return value in ['true', 'yes', '1', 'authorized', 'enabled']
        
        return True
    
    def _extract_wifi_password(self, account: Dict) -> Optional[str]:
        """Extract WiFi password from notes or custom fields"""
        custom_fields = self._extract_custom_fields(account.get('custom_field_data', {}).get('entities', []))
        
        wifi_password_fields = ['wifi_password', 'wireless_password', 'network_password', 'ssid_password']
        for field_name in wifi_password_fields:
            if field_name in custom_fields:
                return custom_fields[field_name]
        
        notes = self._extract_notes(account.get('notes', {}).get('entities', []))
        if notes:
            import re
            password_patterns = [
                r'wifi[:\s]+([^\s\n]+)',
                r'wireless[:\s]+([^\s\n]+)',
                r'password[:\s]+([^\s\n]+)',
                r'ssid[:\s]+([^\s\n]+)'
            ]
            
            for pattern in password_patterns:
                match = re.search(pattern, notes.lower())
                if match:
                    return match.group(1)
        
        return None
    
    def _extract_hardware_info(self, account: Dict) -> Dict[str, Any]:
        """Extract hardware information from notes or custom fields"""
        hardware = {}
        
        custom_fields = self._extract_custom_fields(account.get('custom_field_data', {}).get('entities', []))
        
        hardware_fields = ['modem', 'router', 'equipment', 'hardware', 'device_model']
        for field_name in hardware_fields:
            if field_name in custom_fields:
                hardware[field_name] = custom_fields[field_name]
        
        notes = self._extract_notes(account.get('notes', {}).get('entities', []))
        if notes:
            import re
            hardware_patterns = {
                'modem': r'modem[:\s]+([^\n]+)',
                'router': r'router[:\s]+([^\n]+)',
                'equipment': r'equipment[:\s]+([^\n]+)'
            }
            
            for hw_type, pattern in hardware_patterns.items():
                match = re.search(pattern, notes.lower())
                if match and hw_type not in hardware:
                    hardware[hw_type] = match.group(1).strip()
        
        return hardware
    
    def get_customer_type(self, customer_data: Dict[str, Any]) -> str:
        """Get customer type from customer data"""
        return customer_data.get('type', 'residential')
    
    def get_customer_hardware(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get customer hardware information"""
        return customer_data.get('hardware', {})
    
    def get_wifi_password(self, customer_data: Dict[str, Any]) -> Optional[str]:
        """Get wifi password for authorized customers"""
        if customer_data.get('wifi_access_authorized', False):
            return customer_data.get('wifi_password')
        return None

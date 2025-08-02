#!/usr/bin/env python3
"""Test script to verify Sonar customer lookup functionality"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from customer_data import CustomerDatabase
import logging

def test_customer_lookup():
    """Test customer lookup with various phone number formats"""
    logging.basicConfig(level=logging.INFO)
    
    customer_db = CustomerDatabase()
    
    test_numbers = [
        "6186944239",
        "(618) 694-4239",
        "+1 618-694-4239",
        "618.694.4239",
        "6189226759",
        "(618) 922-6759"
    ]
    
    print("🧪 Testing Sonar customer lookup...")
    
    for phone_number in test_numbers:
        print(f"\n📞 Testing phone number: {phone_number}")
        
        customer_data = customer_db.authenticate_customer(phone_number)
        
        if customer_data:
            print(f"✅ Customer found:")
            print(f"  Name: {customer_data.get('name')}")
            print(f"  Account ID: {customer_data.get('account_id')}")
            print(f"  Type: {customer_data.get('type')}")
            print(f"  Contact: {customer_data.get('contact_name')} ({customer_data.get('contact_role')})")
            print(f"  WiFi Access: {customer_data.get('wifi_access_authorized')}")
            
            wifi_password = customer_db.get_wifi_password(customer_data)
            if wifi_password:
                print(f"  WiFi Password: {wifi_password}")
            
            hardware = customer_db.get_customer_hardware(customer_data)
            if hardware:
                print(f"  Hardware: {hardware}")
            
            if customer_data.get('notes'):
                print(f"  Notes: {customer_data.get('notes')[:100]}...")
        else:
            print("❌ Customer not found")
    
    print("\n🎉 Customer lookup testing complete!")

if __name__ == "__main__":
    test_customer_lookup()

#!/usr/bin/env python3
"""Test script to verify the Sonar API integration functionality"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from customer_data import CustomerDatabase
from sonar_client import SonarClient
from dotenv import load_dotenv

def test_customer_database():
    """Test customer database functionality"""
    print("Testing CustomerDatabase...")
    
    db = CustomerDatabase()
    db.add_sample_data()
    
    customer = db.authenticate_customer('+15551234567')
    assert customer is not None, "Customer authentication failed"
    assert customer['name'] == 'John Doe', "Customer name mismatch"
    print("✅ Customer authentication working")
    
    wifi = db.get_wifi_password(customer)
    assert wifi == 'MySecureWifi123', "WiFi password access failed"
    print("✅ WiFi password access working")
    
    customer_type = db.get_customer_type(customer)
    assert customer_type == 'residential', "Customer type detection failed"
    print("✅ Customer type detection working")
    
    hardware = db.get_customer_hardware(customer)
    assert 'modem' in hardware, "Hardware information missing"
    print("✅ Hardware information retrieval working")

def test_environment_config():
    """Test environment configuration loading"""
    print("Testing environment configuration...")
    
    load_dotenv()
    
    escalation_keywords = os.getenv('ESCALATION_KEYWORDS', '').split(',')
    keywords = [k.strip() for k in escalation_keywords if k.strip()]
    assert len(keywords) > 0, "Escalation keywords not loaded"
    print(f"✅ Escalation keywords loaded: {keywords}")
    
    api_url = os.getenv('SONAR_API_URL')
    assert api_url is not None, "Sonar API URL not configured"
    print(f"✅ Sonar API URL configured: {api_url}")

def test_sonar_client():
    """Test Sonar client initialization"""
    print("Testing SonarClient...")
    
    client = SonarClient()
    assert client.api_url is not None, "Sonar API URL not set"
    assert client.headers is not None, "Sonar headers not configured"
    print("✅ SonarClient initialization working")

if __name__ == "__main__":
    try:
        test_customer_database()
        test_environment_config()
        test_sonar_client()
        print("\n🎉 All tests passed! Integration is ready.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

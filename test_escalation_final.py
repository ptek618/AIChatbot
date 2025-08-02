#!/usr/bin/env python3
"""Final test to verify escalation works with updated code"""

import requests
import time

def test_escalation_endpoint():
    """Test escalation via SMS endpoint"""
    print("🧪 Testing escalation endpoint with updated code...")
    
    url = "http://localhost:5000/sms"
    data = {
        "From": "+16186944239",
        "Body": "urgent help my internet is down"
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if "ticket" in response.text.lower() and "escalated" in response.text.lower():
            print("✅ Escalation working correctly!")
            return True
        else:
            print("❌ Escalation still failing")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    test_escalation_endpoint()

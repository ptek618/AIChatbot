import requests
from typing import Dict, Optional, Any
import json
from datetime import datetime
import random

class SonarIntegration:
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = api_url or "https://api.sonar.protek.com"
        self.api_key = api_key or "sonar_demo_key_12345"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_customer_info(self, customer_id: str) -> Dict[str, Any]:
        return {
            "customer_id": customer_id,
            "name": "John Doe",
            "service_type": "fiber",
            "account_status": "active",
            "service_address": "123 Main St, Anytown, ST 12345",
            "plan": "Fiber 100/100 Mbps",
            "monthly_fee": "$79.99",
            "installation_date": "2023-06-15",
            "equipment": {
                "modem_model": "Nokia G-240W-C",
                "modem_serial": "NK240WC123456",
                "modem_status": "online",
                "firmware_version": "3.2.1",
                "last_seen": datetime.now().isoformat()
            },
            "service_metrics": {
                "uptime_percentage": 99.8,
                "avg_download_speed": "98.5 Mbps",
                "avg_upload_speed": "97.2 Mbps",
                "latency": "5ms"
            }
        }
    
    def check_service_status(self, customer_id: str) -> Dict[str, Any]:
        return {
            "customer_id": customer_id,
            "service_status": "active",
            "network_status": "✅ No area outages detected",
            "outages": [],
            "maintenance_windows": [],
            "signal_quality": {
                "optical_power": "-12.5 dBm (Good)",
                "downstream": "excellent",
                "upstream": "good",
                "latency": "5ms",
                "packet_loss": "0%"
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def get_wifi_credentials(self, customer_id: str) -> Dict[str, str]:
        return {
            "network_name": "ProTek_Fiber_5G",
            "password": "ProTek2024Secure!",
            "network_name_2g": "ProTek_Fiber_2G",
            "password_2g": "ProTek2024Secure!",
            "guest_network": "ProTek_Guest",
            "guest_password": "Welcome123",
            "admin_url": "http://192.168.1.1",
            "admin_username": "admin",
            "admin_password": "admin123"
        }
    
    def run_speed_test(self, customer_id: str) -> Dict[str, Any]:
        download_speed = random.uniform(85, 105)
        upload_speed = random.uniform(80, 100)
        
        return {
            "customer_id": customer_id,
            "test_timestamp": datetime.now().isoformat(),
            "download_speed": f"{download_speed:.1f} Mbps",
            "upload_speed": f"{upload_speed:.1f} Mbps",
            "latency": f"{random.uniform(3, 8):.1f}ms",
            "jitter": f"{random.uniform(0.5, 2.0):.1f}ms",
            "packet_loss": "0%",
            "server_location": "Local Test Server"
        }
    
    def create_ticket(self, customer_id: str, issue_type: str, description: str, priority: str = "medium") -> Dict[str, Any]:
        ticket_id = f"SONAR-{random.randint(100000, 999999)}"
        
        ticket_data = {
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "issue_type": issue_type,
            "description": description,
            "priority": priority,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "assigned_to": "support_team",
            "estimated_resolution": "2-4 hours"
        }
        
        self.send_ticket_email(ticket_data)
        
        return ticket_data
    
    def send_ticket_email(self, ticket_data: Dict[str, Any]):
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        try:
            msg = MIMEMultipart()
            msg['From'] = "chatbot@protekweb.com"
            msg['To'] = "support@protekweb.com"
            msg['Subject'] = f"New Support Ticket: {ticket_data['ticket_id']}"
            
            body = f"""
New support ticket created via AI Chatbot:

Ticket ID: {ticket_data['ticket_id']}
Customer ID: {ticket_data['customer_id']}
Issue Type: {ticket_data['issue_type']}
Priority: {ticket_data['priority']}
Description: {ticket_data['description']}
Created: {ticket_data['created_at']}

This ticket should be imported into Sonar for tracking.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('localhost', 587)
            text = msg.as_string()
            server.sendmail("chatbot@protekweb.com", "support@protekweb.com", text)
            server.quit()
            
        except Exception as e:
            print(f"Failed to send ticket email: {e}")

class UISPIntegration:
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = api_url or "https://uisp.protek.com"
        self.api_key = api_key or "uisp_demo_key_67890"
        self.headers = {
            "X-Auth-Token": self.api_key,
            "Content-Type": "application/json"
        }
    
    def get_customer_equipment(self, customer_id: str) -> Dict[str, Any]:
        signal_strength = random.uniform(-70, -55)
        signal_quality = max(0, min(100, (signal_strength + 100) * 2))
        
        return {
            "customer_id": customer_id,
            "equipment": {
                "cpe_model": "Ubiquiti NanoStation AC",
                "cpe_serial": "UBNT-NS-AC-789012",
                "cpe_status": "connected",
                "signal_strength": f"{signal_strength:.1f} dBm",
                "signal_quality": f"{signal_quality:.0f}%",
                "last_seen": datetime.now().isoformat(),
                "ip_address": f"10.1.{random.randint(100, 200)}.{random.randint(10, 250)}",
                "mac_address": "04:18:D6:12:34:56",
                "firmware_version": "WA.v8.7.4"
            },
            "tower_info": {
                "tower_name": "Tower_North_01",
                "tower_location": "North Hill Site",
                "distance": f"{random.uniform(1.5, 4.0):.1f} miles",
                "azimuth": f"{random.randint(30, 60)}°",
                "elevation": f"{random.randint(5, 15)}°"
            },
            "performance_metrics": {
                "throughput_down": f"{random.uniform(40, 60):.1f} Mbps",
                "throughput_up": f"{random.uniform(15, 25):.1f} Mbps",
                "latency": f"{random.uniform(8, 15):.1f}ms",
                "uptime": "99.2%"
            }
        }
    
    def check_signal_quality(self, customer_id: str) -> Dict[str, Any]:
        signal_strength = random.uniform(-70, -55)
        signal_quality = max(0, min(100, (signal_strength + 100) * 2))
        
        return {
            "customer_id": customer_id,
            "signal_strength": f"{signal_strength:.1f} dBm",
            "signal_quality": f"{signal_quality:.0f}%",
            "connection_status": "stable" if signal_quality > 70 else "unstable",
            "throughput": {
                "download": f"{random.uniform(35, 55):.0f} Mbps",
                "upload": f"{random.uniform(12, 20):.0f} Mbps"
            },
            "latency": f"{random.uniform(8, 15):.1f}ms",
            "packet_loss": f"{random.uniform(0, 2):.1f}%",
            "interference_level": "low" if signal_quality > 80 else "moderate",
            "weather_impact": "none",
            "last_updated": datetime.now().isoformat()
        }
    
    def get_tower_status(self, tower_name: str) -> Dict[str, Any]:
        return {
            "tower_name": tower_name,
            "status": "operational",
            "uptime": "99.8%",
            "connected_customers": random.randint(45, 85),
            "capacity_utilization": f"{random.uniform(35, 75):.0f}%",
            "weather_conditions": "clear",
            "maintenance_scheduled": False,
            "last_updated": datetime.now().isoformat()
        }

class VerizonPortalIntegration:
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = api_url or "https://portal.verizon.com/api"
        self.api_key = api_key or "verizon_demo_key_54321"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_device_status(self, customer_id: str) -> Dict[str, Any]:
        signal_bars = random.randint(3, 5)
        data_usage_gb = random.uniform(15, 45)
        
        return {
            "customer_id": customer_id,
            "device": {
                "model": "Verizon Jetpack MiFi 8800L",
                "imei": "123456789012345",
                "phone_number": "+1-555-0123",
                "status": "active",
                "signal_bars": signal_bars,
                "signal_strength": f"{random.uniform(-85, -65):.0f} dBm",
                "network_type": "4G LTE",
                "battery_level": f"{random.randint(45, 95)}%",
                "last_seen": datetime.now().isoformat()
            },
            "network_info": {
                "carrier": "Verizon Wireless",
                "tower_location": "Cell Tower 4G-VZ-789",
                "coverage_type": "4G LTE",
                "roaming": False
            },
            "data_usage": {
                "current_month": f"{data_usage_gb:.1f} GB",
                "plan_limit": "Unlimited",
                "billing_cycle_end": "2024-08-15"
            }
        }
    
    def check_network_coverage(self, customer_id: str, location: str = None) -> Dict[str, Any]:
        return {
            "customer_id": customer_id,
            "location": location or "Customer Location",
            "coverage_quality": "excellent",
            "network_type": "4G LTE",
            "expected_speeds": {
                "download": "25-50 Mbps",
                "upload": "5-15 Mbps"
            },
            "tower_distance": f"{random.uniform(0.5, 2.5):.1f} miles",
            "congestion_level": "low",
            "weather_impact": "none",
            "last_updated": datetime.now().isoformat()
        }
    
    def run_network_diagnostics(self, customer_id: str) -> Dict[str, Any]:
        return {
            "customer_id": customer_id,
            "test_timestamp": datetime.now().isoformat(),
            "network_status": "connected",
            "signal_quality": f"{random.uniform(70, 95):.0f}%",
            "data_session": "active",
            "ip_address": f"100.{random.randint(64, 127)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
            "dns_servers": ["8.8.8.8", "8.8.4.4"],
            "ping_test": f"{random.uniform(25, 45):.0f}ms",
            "throughput_test": {
                "download": f"{random.uniform(20, 45):.1f} Mbps",
                "upload": f"{random.uniform(8, 18):.1f} Mbps"
            }
        }

class BackendIntegrationManager:
    def __init__(self):
        self.sonar = SonarIntegration()
        self.uisp = UISPIntegration()
        self.verizon = VerizonPortalIntegration()
    
    def run_diagnostics(self, customer_id: str, service_type: str) -> Dict[str, Any]:
        if service_type == "fiber":
            return self.sonar.check_service_status(customer_id)
        elif service_type == "fixed_wireless":
            equipment_data = self.uisp.get_customer_equipment(customer_id)
            signal_data = self.uisp.check_signal_quality(customer_id)
            return {
                "network_status": "✅ No area outages detected",
                "tower_status": "✅ Operating normally",
                "signal_path": "🔍 Checking your connection...",
                "signal_strength": signal_data.get("signal_strength", "-65 dBm (Good)"),
                "equipment_status": equipment_data.get("equipment", {}).get("cpe_status", "connected")
            }
        elif service_type == "lte":
            device_data = self.verizon.get_device_status(customer_id)
            coverage_data = self.verizon.check_network_coverage(customer_id)
            return {
                "network_coverage": "✅ Good signal in your area",
                "device_status": "🔍 Checking your connection...",
                "signal_bars": f"{device_data.get('device', {}).get('signal_bars', 4)}/5 bars",
                "network_type": device_data.get("device", {}).get("network_type", "4G LTE")
            }
        else:
            return {
                "service_status": "🔍 Checking for outages",
                "equipment_health": "🔍 Analyzing your connection",
                "account_status": "🔍 Verifying service details"
            }
    
    def run_speed_diagnostics(self, customer_id: str, service_type: str) -> Dict[str, Any]:
        if service_type == "fiber":
            speed_data = self.sonar.run_speed_test(customer_id)
            return {
                "service_plan": "🔍 Verifying your speed tier",
                "network_load": "🔍 Checking for congestion",
                "equipment_status": "🔍 Analyzing performance",
                "current_speed": f"Download: {speed_data.get('download_speed', 'Testing...')}"
            }
        elif service_type == "fixed_wireless":
            equipment_data = self.uisp.get_customer_equipment(customer_id)
            return {
                "service_plan": "Fixed Wireless 50/20 Mbps",
                "network_load": "Low congestion detected",
                "equipment_status": "Equipment online",
                "current_speed": f"Download: {equipment_data.get('performance_metrics', {}).get('throughput_down', '45 Mbps')}"
            }
        elif service_type == "lte":
            diagnostics = self.verizon.run_network_diagnostics(customer_id)
            return {
                "service_plan": "LTE Unlimited Plan",
                "network_load": "Normal network traffic",
                "equipment_status": "Device connected",
                "current_speed": f"Download: {diagnostics.get('throughput_test', {}).get('download', '25 Mbps')}"
            }
        else:
            return {
                "service_plan": "🔍 Verifying your speed tier",
                "network_load": "🔍 Checking for congestion",
                "equipment_status": "🔍 Analyzing performance",
                "current_speed": "Testing..."
            }
    
    def run_stability_diagnostics(self, customer_id: str, service_type: str) -> Dict[str, Any]:
        return {
            "stability_score": "🔍 Checking for patterns",
            "equipment_health": "🔍 Analyzing performance logs",
            "environmental_factors": "🔍 Checking for interference",
            "recent_outages": "None detected"
        }
    
    def run_general_diagnostics(self, customer_id: str, service_type: str) -> Dict[str, Any]:
        return {
            "service_status": "🔍 Checking for outages",
            "equipment_health": "🔍 Analyzing your connection",
            "account_status": "🔍 Verifying service details"
        }
    
    def verify_customer_identity(self, verification_info: str) -> bool:
        return len(verification_info.strip()) > 5
    
    def get_wifi_credentials(self, customer_id: str, service_type: str) -> Dict[str, str]:
        if service_type == "fiber":
            return self.sonar.get_wifi_credentials(customer_id)
        else:
            return {
                "network_name": "ProTek_WiFi_5G",
                "password": "ProTek2024Secure!",
                "guest_network": "ProTek_Guest",
                "guest_password": "Welcome123"
            }

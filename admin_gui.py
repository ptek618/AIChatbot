from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import json
from datetime import datetime
from typing import Dict, Any
import os

class AdminGUI:
    def __init__(self, app: Flask):
        self.app = app
        self.config_file = "admin_config.json"
        self.load_config()
        self.setup_routes()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "isp_settings": {
                    "company_name": "ProTek Internet",
                    "support_email": "support@protekweb.com",
                    "support_phone": "1-800-PROTEK",
                    "logo_url": "",
                    "primary_color": "#4CAF50",
                    "secondary_color": "#2E7D32"
                },
                "backend_integrations": {
                    "sonar": {
                        "enabled": True,
                        "api_url": "https://api.sonar.protek.com",
                        "api_key": "sonar_demo_key_12345"
                    },
                    "uisp": {
                        "enabled": True,
                        "api_url": "https://uisp.protek.com",
                        "api_key": "uisp_demo_key_67890"
                    },
                    "verizon": {
                        "enabled": True,
                        "api_url": "https://portal.verizon.com/api",
                        "api_key": "verizon_demo_key_54321"
                    }
                },
                "escalation_rules": {
                    "business_response_time": "15 minutes",
                    "enterprise_response_time": "10 minutes",
                    "residential_response_time": "2-4 hours",
                    "northbridge_response_time": "30 minutes"
                },
                "service_types": {
                    "fiber": {"enabled": True, "backend": "sonar"},
                    "fixed_wireless": {"enabled": True, "backend": "uisp"},
                    "lte": {"enabled": True, "backend": "verizon"}
                }
            }
            self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def setup_routes(self):
        @self.app.route('/admin')
        def admin_dashboard():
            return render_template_string(ADMIN_DASHBOARD_TEMPLATE, config=self.config)
        
        @self.app.route('/admin/config', methods=['GET', 'POST'])
        def admin_config():
            if request.method == 'POST':
                data = request.get_json()
                self.config.update(data)
                self.save_config()
                return jsonify({"status": "success", "message": "Configuration updated successfully"})
            return jsonify(self.config)
        
        @self.app.route('/admin/test-integration/<integration>')
        def test_integration(integration):
            if integration == "sonar":
                from backend_integrations import SonarIntegration
                sonar = SonarIntegration(
                    self.config["backend_integrations"]["sonar"]["api_url"],
                    self.config["backend_integrations"]["sonar"]["api_key"]
                )
                try:
                    result = sonar.get_customer_info("test_customer")
                    return jsonify({"status": "success", "data": result})
                except Exception as e:
                    return jsonify({"status": "error", "message": str(e)})
            
            elif integration == "uisp":
                from backend_integrations import UISPIntegration
                uisp = UISPIntegration(
                    self.config["backend_integrations"]["uisp"]["api_url"],
                    self.config["backend_integrations"]["uisp"]["api_key"]
                )
                try:
                    result = uisp.get_customer_equipment("test_customer")
                    return jsonify({"status": "success", "data": result})
                except Exception as e:
                    return jsonify({"status": "error", "message": str(e)})
            
            elif integration == "verizon":
                from backend_integrations import VerizonPortalIntegration
                verizon = VerizonPortalIntegration(
                    self.config["backend_integrations"]["verizon"]["api_url"],
                    self.config["backend_integrations"]["verizon"]["api_key"]
                )
                try:
                    result = verizon.get_device_status("test_customer")
                    return jsonify({"status": "success", "data": result})
                except Exception as e:
                    return jsonify({"status": "error", "message": str(e)})
            
            return jsonify({"status": "error", "message": "Unknown integration"})

ADMIN_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ProTek AI Chatbot - Admin Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
        }
        
        .header {
            background: linear-gradient(135deg, #2E7D32, #4CAF50);
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .card h2 {
            color: #2E7D32;
            margin-bottom: 15px;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }
        
        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            border-color: #4CAF50;
            outline: none;
        }
        
        .btn {
            background: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin-right: 10px;
        }
        
        .btn:hover {
            background: #45a049;
        }
        
        .btn-test {
            background: #2196F3;
        }
        
        .btn-test:hover {
            background: #1976D2;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-enabled {
            background: #4CAF50;
        }
        
        .status-disabled {
            background: #f44336;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .integration-card {
            border-left: 4px solid #4CAF50;
        }
        
        .test-result {
            margin-top: 10px;
            padding: 10px;
            border-radius: 5px;
            display: none;
        }
        
        .test-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .test-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌐 ProTek AI Chatbot - Admin Dashboard</h1>
        <p>Multi-ISP Configuration & Management System</p>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>🏢 ISP Settings</h2>
            <div class="grid">
                <div class="form-group">
                    <label>Company Name</label>
                    <input type="text" id="company_name" value="{{ config.isp_settings.company_name }}">
                </div>
                <div class="form-group">
                    <label>Support Email</label>
                    <input type="email" id="support_email" value="{{ config.isp_settings.support_email }}">
                </div>
                <div class="form-group">
                    <label>Support Phone</label>
                    <input type="text" id="support_phone" value="{{ config.isp_settings.support_phone }}">
                </div>
                <div class="form-group">
                    <label>Logo URL</label>
                    <input type="url" id="logo_url" value="{{ config.isp_settings.logo_url }}">
                </div>
                <div class="form-group">
                    <label>Primary Color</label>
                    <input type="color" id="primary_color" value="{{ config.isp_settings.primary_color }}">
                </div>
                <div class="form-group">
                    <label>Secondary Color</label>
                    <input type="color" id="secondary_color" value="{{ config.isp_settings.secondary_color }}">
                </div>
            </div>
            <button class="btn" onclick="saveISPSettings()">Save ISP Settings</button>
        </div>
        
        <div class="card">
            <h2>🔌 Backend Integrations</h2>
            <div class="grid">
                <div class="card integration-card">
                    <h3>
                        <span class="status-indicator {{ 'status-enabled' if config.backend_integrations.sonar.enabled else 'status-disabled' }}"></span>
                        Sonar Integration
                    </h3>
                    <div class="form-group">
                        <label>API URL</label>
                        <input type="url" id="sonar_api_url" value="{{ config.backend_integrations.sonar.api_url }}">
                    </div>
                    <div class="form-group">
                        <label>API Key</label>
                        <input type="password" id="sonar_api_key" value="{{ config.backend_integrations.sonar.api_key }}">
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="sonar_enabled" {{ 'checked' if config.backend_integrations.sonar.enabled else '' }}>
                            Enable Sonar Integration
                        </label>
                    </div>
                    <button class="btn btn-test" onclick="testIntegration('sonar')">Test Connection</button>
                    <div id="sonar-test-result" class="test-result"></div>
                </div>
                
                <div class="card integration-card">
                    <h3>
                        <span class="status-indicator {{ 'status-enabled' if config.backend_integrations.uisp.enabled else 'status-disabled' }}"></span>
                        UISP Integration
                    </h3>
                    <div class="form-group">
                        <label>API URL</label>
                        <input type="url" id="uisp_api_url" value="{{ config.backend_integrations.uisp.api_url }}">
                    </div>
                    <div class="form-group">
                        <label>API Key</label>
                        <input type="password" id="uisp_api_key" value="{{ config.backend_integrations.uisp.api_key }}">
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="uisp_enabled" {{ 'checked' if config.backend_integrations.uisp.enabled else '' }}>
                            Enable UISP Integration
                        </label>
                    </div>
                    <button class="btn btn-test" onclick="testIntegration('uisp')">Test Connection</button>
                    <div id="uisp-test-result" class="test-result"></div>
                </div>
                
                <div class="card integration-card">
                    <h3>
                        <span class="status-indicator {{ 'status-enabled' if config.backend_integrations.verizon.enabled else 'status-disabled' }}"></span>
                        Verizon Portal Integration
                    </h3>
                    <div class="form-group">
                        <label>API URL</label>
                        <input type="url" id="verizon_api_url" value="{{ config.backend_integrations.verizon.api_url }}">
                    </div>
                    <div class="form-group">
                        <label>API Key</label>
                        <input type="password" id="verizon_api_key" value="{{ config.backend_integrations.verizon.api_key }}">
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="verizon_enabled" {{ 'checked' if config.backend_integrations.verizon.enabled else '' }}>
                            Enable Verizon Integration
                        </label>
                    </div>
                    <button class="btn btn-test" onclick="testIntegration('verizon')">Test Connection</button>
                    <div id="verizon-test-result" class="test-result"></div>
                </div>
            </div>
            <button class="btn" onclick="saveIntegrationSettings()">Save Integration Settings</button>
        </div>
        
        <div class="card">
            <h2>⚡ Escalation Rules</h2>
            <div class="grid">
                <div class="form-group">
                    <label>Business Response Time</label>
                    <input type="text" id="business_response_time" value="{{ config.escalation_rules.business_response_time }}">
                </div>
                <div class="form-group">
                    <label>Enterprise Response Time</label>
                    <input type="text" id="enterprise_response_time" value="{{ config.escalation_rules.enterprise_response_time }}">
                </div>
                <div class="form-group">
                    <label>Residential Response Time</label>
                    <input type="text" id="residential_response_time" value="{{ config.escalation_rules.residential_response_time }}">
                </div>
                <div class="form-group">
                    <label>Northbridge Response Time</label>
                    <input type="text" id="northbridge_response_time" value="{{ config.escalation_rules.northbridge_response_time }}">
                </div>
            </div>
            <button class="btn" onclick="saveEscalationRules()">Save Escalation Rules</button>
        </div>
        
        <div class="card">
            <h2>🌐 Service Types Configuration</h2>
            <div class="grid">
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="fiber_enabled" {{ 'checked' if config.service_types.fiber.enabled else '' }}>
                        Enable Fiber Service
                    </label>
                    <select id="fiber_backend">
                        <option value="sonar" {{ 'selected' if config.service_types.fiber.backend == 'sonar' else '' }}>Sonar</option>
                        <option value="uisp" {{ 'selected' if config.service_types.fiber.backend == 'uisp' else '' }}>UISP</option>
                        <option value="verizon" {{ 'selected' if config.service_types.fiber.backend == 'verizon' else '' }}>Verizon</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="fixed_wireless_enabled" {{ 'checked' if config.service_types.fixed_wireless.enabled else '' }}>
                        Enable Fixed Wireless Service
                    </label>
                    <select id="fixed_wireless_backend">
                        <option value="sonar" {{ 'selected' if config.service_types.fixed_wireless.backend == 'sonar' else '' }}>Sonar</option>
                        <option value="uisp" {{ 'selected' if config.service_types.fixed_wireless.backend == 'uisp' else '' }}>UISP</option>
                        <option value="verizon" {{ 'selected' if config.service_types.fixed_wireless.backend == 'verizon' else '' }}>Verizon</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="lte_enabled" {{ 'checked' if config.service_types.lte.enabled else '' }}>
                        Enable LTE Service
                    </label>
                    <select id="lte_backend">
                        <option value="sonar" {{ 'selected' if config.service_types.lte.backend == 'sonar' else '' }}>Sonar</option>
                        <option value="uisp" {{ 'selected' if config.service_types.lte.backend == 'uisp' else '' }}>UISP</option>
                        <option value="verizon" {{ 'selected' if config.service_types.lte.backend == 'verizon' else '' }}>Verizon</option>
                    </select>
                </div>
            </div>
            <button class="btn" onclick="saveServiceTypes()">Save Service Types</button>
        </div>
    </div>
    
    <script>
        function saveISPSettings() {
            const config = {
                isp_settings: {
                    company_name: document.getElementById('company_name').value,
                    support_email: document.getElementById('support_email').value,
                    support_phone: document.getElementById('support_phone').value,
                    logo_url: document.getElementById('logo_url').value,
                    primary_color: document.getElementById('primary_color').value,
                    secondary_color: document.getElementById('secondary_color').value
                }
            };
            
            saveConfig(config, 'ISP settings');
        }
        
        function saveIntegrationSettings() {
            const config = {
                backend_integrations: {
                    sonar: {
                        enabled: document.getElementById('sonar_enabled').checked,
                        api_url: document.getElementById('sonar_api_url').value,
                        api_key: document.getElementById('sonar_api_key').value
                    },
                    uisp: {
                        enabled: document.getElementById('uisp_enabled').checked,
                        api_url: document.getElementById('uisp_api_url').value,
                        api_key: document.getElementById('uisp_api_key').value
                    },
                    verizon: {
                        enabled: document.getElementById('verizon_enabled').checked,
                        api_url: document.getElementById('verizon_api_url').value,
                        api_key: document.getElementById('verizon_api_key').value
                    }
                }
            };
            
            saveConfig(config, 'Integration settings');
        }
        
        function saveEscalationRules() {
            const config = {
                escalation_rules: {
                    business_response_time: document.getElementById('business_response_time').value,
                    enterprise_response_time: document.getElementById('enterprise_response_time').value,
                    residential_response_time: document.getElementById('residential_response_time').value,
                    northbridge_response_time: document.getElementById('northbridge_response_time').value
                }
            };
            
            saveConfig(config, 'Escalation rules');
        }
        
        function saveServiceTypes() {
            const config = {
                service_types: {
                    fiber: {
                        enabled: document.getElementById('fiber_enabled').checked,
                        backend: document.getElementById('fiber_backend').value
                    },
                    fixed_wireless: {
                        enabled: document.getElementById('fixed_wireless_enabled').checked,
                        backend: document.getElementById('fixed_wireless_backend').value
                    },
                    lte: {
                        enabled: document.getElementById('lte_enabled').checked,
                        backend: document.getElementById('lte_backend').value
                    }
                }
            };
            
            saveConfig(config, 'Service types');
        }
        
        function saveConfig(config, section) {
            fetch('/admin/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(section + ' saved successfully!');
                    location.reload();
                } else {
                    alert('Error saving ' + section + ': ' + data.message);
                }
            })
            .catch(error => {
                alert('Error saving ' + section + ': ' + error);
            });
        }
        
        function testIntegration(integration) {
            const resultDiv = document.getElementById(integration + '-test-result');
            resultDiv.style.display = 'block';
            resultDiv.className = 'test-result';
            resultDiv.innerHTML = 'Testing connection...';
            
            fetch('/admin/test-integration/' + integration)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    resultDiv.className = 'test-result test-success';
                    resultDiv.innerHTML = '✅ Connection successful! Test data retrieved.';
                } else {
                    resultDiv.className = 'test-result test-error';
                    resultDiv.innerHTML = '❌ Connection failed: ' + data.message;
                }
            })
            .catch(error => {
                resultDiv.className = 'test-result test-error';
                resultDiv.innerHTML = '❌ Connection failed: ' + error;
            });
        }
    </script>
</body>
</html>
"""

# ProTek AI Chatbot with Sonar Integration

A Flask-based SMS chatbot for ProTek ISP that integrates with Sonar software for automatic ticket creation and customer support.

## Features

- **Customer Authentication**: Authenticates customers via phone number lookup
- **Escalation Detection**: Automatically detects escalation keywords and creates Sonar tickets
- **Secure WiFi Access**: Provides WiFi passwords only to authorized customers
- **Hardware Information**: Displays customer equipment details based on account type
- **Customer Type Detection**: Supports business and residential customer types
- **Sonar API Integration**: Creates internal tickets via GraphQL API

## Setup

1. Install dependencies:
   ```bash
   python setup.py
   ```

2. Configure environment variables in `.env`:
   ```
   SONAR_API_URL=https://api.sonar.software/graphql
   SONAR_API_TOKEN=your_sonar_api_token_here
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   ESCALATION_KEYWORDS=escalate,urgent,emergency,manager,supervisor,help,issue,problem,broken,down,outage
   DEFAULT_TICKET_PRIORITY=MEDIUM
   DEFAULT_TICKET_STATUS=OPEN
   ```

3. Run the application:
   ```bash
   python app.py
   ```

## Customer Data Format

The system uses a JSON file (`customers.json`) to store customer information:

```json
{
  "5551234567": {
    "name": "John Doe",
    "type": "residential",
    "account_id": "12345",
    "wifi_access_authorized": true,
    "wifi_password": "MySecureWifi123",
    "hardware": {
      "modem": "Netgear CM1000",
      "router": "ASUS AX6000"
    }
  }
}
```

## SMS Commands

- **"hi" or "hello"**: Basic greeting with personalized response
- **"help"**: Shows available commands and customer account type
- **"wifi" or "password"**: Returns WiFi password (if authorized)
- **"hardware" or "equipment"**: Shows customer equipment information
- **Escalation keywords**: Creates Sonar ticket automatically

## Security Features

- Phone number authentication required for all operations
- WiFi passwords only provided to customers with `wifi_access_authorized: true`
- Customer type verification for appropriate support information
- Secure API token handling via environment variables

## Testing

The system includes sample customer data for testing:
- Phone: 5551234567 (residential customer with WiFi access)
- Phone: 5559876543 (business customer with WiFi access)

## Deployment

Configure Twilio webhook to point to your server's `/sms` endpoint.

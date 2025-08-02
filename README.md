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

## Customer Data Structure

The chatbot now reads customer data directly from Sonar's database using GraphQL queries. Customer authentication is performed by:

1. **Phone Number Lookup**: Normalizes incoming phone numbers and searches Sonar's PhoneNumber entities
2. **Account Resolution**: Follows the PhoneNumber -> Contact -> Account relationship chain
3. **Data Extraction**: Extracts customer information from Account notes and custom fields

### WiFi Password Storage

WiFi passwords can be stored in Sonar using either:
- **Custom Fields**: Create custom fields named `wifi_password`, `wireless_password`, or `network_password`
- **Account Notes**: Include password information in account notes using patterns like "WiFi: password123"

### Hardware Information Storage

Hardware information can be stored using:
- **Custom Fields**: Create fields for `modem`, `router`, `equipment`
- **Account Notes**: Include hardware details in notes using patterns like "Modem: Netgear CM1000"

### Customer Authorization

WiFi password access is controlled by:
- Custom fields named `wifi_access`, `wifi_authorized`, or `password_access`
- Default authorization can be configured via `DEFAULT_WIFI_ACCESS` environment variable

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

Test the Sonar customer lookup functionality:
```bash
python test_sonar_customer_lookup.py
```

Test the complete SMS integration:
```bash
python app.py &
python test_sms_flows.py
```

## Deployment

Configure Twilio webhook to point to your server's `/sms` endpoint.

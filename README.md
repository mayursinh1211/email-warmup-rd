# Email Warmup System

A sophisticated email warmup system built with FastAPI and MongoDB to help gradually increase email sender reputation and deliverability.

## Features

- 📧 Automated email warmup campaigns
- 📈 Progressive sending volume increase
- 📊 Deliverability monitoring
- 🔐 Secure authentication system
- 📱 RESTful API endpoints
- 📝 Comprehensive logging
- 🔄 Automatic warmup stage progression

## Tech Stack

- **Backend Framework:** FastAPI
- **Database:** MongoDB
- **Authentication:** JWT
- **Email Handling:** aiosmtplib, aioimaplib
- **Testing:** pytest
- **Documentation:** OpenAPI (Swagger)

## Prerequisites

- Python 3.9+
- MongoDB 4.4+
- SMTP Server access
- IMAP Server access

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mayursinh1211/email-warmup-rd.git
cd email-warmup-rd
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env file with your configurations
```

## Configuration

Create a `.env` file in the root directory with the following variables:

```env
# MongoDB Settings
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=email_warmup

# JWT Settings
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Settings
SMTP_TLS=True
SMTP_PORT=587
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
```

## Running the Application

1. Start the application:
```bash
python run.py
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/token` - Get access token

### Email Campaigns
- `POST /api/v1/campaigns/` - Create new campaign
- `GET /api/v1/campaigns/{campaign_id}` - Get campaign details
- `PUT /api/v1/campaigns/{campaign_id}` - Update campaign
- `DELETE /api/v1/campaigns/{campaign_id}` - Delete campaign

### Email Accounts
- `POST /api/v1/email-accounts/` - Add new email account
- `GET /api/v1/email-accounts/` - List email accounts
- `PUT /api/v1/email-accounts/{account_id}` - Update email account
- `DELETE /api/v1/email-accounts/{account_id}` - Delete email account

## Warmup Strategy

The system uses a progressive warmup strategy:

1. **Stage 1**: 5-10 emails per day
2. **Stage 2**: 10-25 emails per day
3. **Stage 3**: 25-50 emails per day
4. **Stage 4**: 50-75 emails per day
5. **Stage 5**: 75-100 emails per day

Progression criteria:
- 95% delivery rate
- Minimum 7 days in current stage
- No spam flags

## Testing

Run the test suite:
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature ▋

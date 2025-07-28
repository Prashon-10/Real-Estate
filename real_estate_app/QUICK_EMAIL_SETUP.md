# Real Email Delivery Setup Guide

## Quick Setup for Real Email Delivery

To enable real email delivery for user registration verification, follow these steps:

### Step 1: Get Email Credentials

#### For Gmail (Recommended)
1. **Enable 2-Factor Authentication** on your Google account
2. **Generate an App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character app password
3. **Use the App Password** (not your regular Gmail password)

#### For Outlook/Hotmail
1. Use your regular Outlook password
2. If 2FA is enabled, generate an App Password

#### For Yahoo
1. Enable "Less secure app access" or use App Password
2. Generate App Password: https://login.yahoo.com/account/security

### Step 2: Update .env File

Edit the `.env` file in your project root and update these settings:

```bash
# Change from console to smtp
EMAIL_BACKEND=smtp

# Add your email credentials
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_16_character_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

**For other providers:**
- **Outlook**: `EMAIL_HOST=smtp-mail.outlook.com`
- **Yahoo**: `EMAIL_HOST=smtp.mail.yahoo.com`

### Step 3: Test Configuration

```bash
python test_email_config.py
```

Enter your email address when prompted to receive a test email.

### Step 4: Test User Registration

1. Start the development server:
   ```bash
   python manage.py runserver
   ```

2. Go to: http://127.0.0.1:8000/accounts/register/

3. Register with a valid email address

4. Check your email inbox for the verification email

## Common Issues and Solutions

### Gmail Authentication Failed
- **Solution**: Use App Password, not regular password
- **Check**: 2FA must be enabled first

### Emails Not Received
- **Check**: Spam/Junk folder
- **Check**: Email address spelling
- **Check**: Provider SMTP settings

### Connection Refused
- **Check**: Internet connection
- **Check**: Firewall settings
- **Check**: SMTP host and port

### Permission Denied
- **Gmail**: Enable "Less secure app access" or use App Password
- **Outlook**: Check account security settings

## Security Notes

- **Never commit** your `.env` file to version control
- **Use App Passwords** instead of regular passwords
- **Enable 2FA** on your email account
- **Rotate credentials** regularly

## Alternative: Using Email Services

For production, consider using email services like:
- **SendGrid** (99.9% delivery rate)
- **Mailgun** (Developer-friendly)
- **Amazon SES** (Cost-effective)
- **Postmark** (Fast delivery)

These services provide better deliverability and detailed analytics.

## Testing the Complete Flow

1. **Console Mode** (Development):
   ```bash
   EMAIL_BACKEND=console
   ```
   Emails are printed to console for testing

2. **SMTP Mode** (Production):
   ```bash
   EMAIL_BACKEND=smtp
   ```
   Real emails are sent to users

## Need Help?

Run the interactive setup:
```bash
python setup_email.py
```

Or check the detailed documentation in `docs/email_setup_guide.md`

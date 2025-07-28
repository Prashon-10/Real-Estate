# Email Configuration Setup Guide

This guide will help you configure real email delivery for the Real Estate application's email verification system.

## Current Issue
The application is currently configured to use Django's console email backend, which only prints emails to the terminal instead of actually sending them. To enable real email delivery, you need to configure an SMTP backend.

## Quick Setup Options

### Option 1: Gmail (Recommended for Development/Testing)

1. **Create/Use a Gmail account** for your application
2. **Enable 2-Factor Authentication** on your Gmail account
3. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
   - Copy the generated 16-character password

4. **Set Environment Variables**:
   Create a `.env` file in your project root with:
   ```env
   USE_CONSOLE_EMAIL=false
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=true
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-character-app-password
   DEFAULT_FROM_EMAIL=RealEstate Platform <your-email@gmail.com>
   ```

### Option 2: Outlook/Hotmail

1. **Use your Outlook/Hotmail account**
2. **Set Environment Variables**:
   ```env
   USE_CONSOLE_EMAIL=false
   EMAIL_HOST=smtp.live.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=true
   EMAIL_HOST_USER=your-email@outlook.com
   EMAIL_HOST_PASSWORD=your-password
   DEFAULT_FROM_EMAIL=RealEstate Platform <your-email@outlook.com>
   ```

### Option 3: SendGrid (Recommended for Production)

1. **Sign up for SendGrid** (free tier available)
2. **Create an API key** in SendGrid dashboard
3. **Set Environment Variables**:
   ```env
   USE_CONSOLE_EMAIL=false
   EMAIL_HOST=smtp.sendgrid.net
   EMAIL_PORT=587
   EMAIL_USE_TLS=true
   EMAIL_HOST_USER=apikey
   EMAIL_HOST_PASSWORD=your-sendgrid-api-key
   DEFAULT_FROM_EMAIL=RealEstate Platform <noreply@yourdomain.com>
   ```

## Environment Variable Setup

### Method 1: Using python-decouple (Recommended)

1. **Install python-decouple**:
   ```bash
   pip install python-decouple
   ```

2. **Update settings.py** (add at the top):
   ```python
   from decouple import config
   ```

3. **Create `.env` file** in your project root using the `.env.example` template

### Method 2: Using OS Environment Variables

Set the environment variables in your system or IDE:
- Windows PowerShell: `$env:EMAIL_HOST_USER="your-email@gmail.com"`
- Command Prompt: `set EMAIL_HOST_USER=your-email@gmail.com`
- VS Code: Add to launch.json env configuration

### Method 3: Direct Configuration (Not Recommended for Production)

Temporarily set values directly in `settings.py` for testing:

```python
# For testing only - don't commit these values!
USE_CONSOLE_EMAIL = False
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## Testing Email Delivery

1. **Start your Django development server**:
   ```bash
   python manage.py runserver
   ```

2. **Register a new user** with a real email address

3. **Check your email** for the verification message

4. **Check the Django console** for any error messages

## Troubleshooting

### Common Issues and Solutions

#### Gmail Authentication Error
- **Problem**: "Username and Password not accepted"
- **Solution**: Make sure you're using an App Password, not your regular Gmail password
- **Check**: 2-Factor Authentication must be enabled to generate App Passwords

#### Connection Timeout
- **Problem**: Email sending times out
- **Solution**: Check firewall settings, try different ports (465 for SSL)
- **Alternative**: Try a different email provider

#### "SMTPAuthenticationError"
- **Problem**: Invalid credentials
- **Solution**: Double-check your email and password/app password
- **Check**: Ensure the email account allows SMTP access

#### Environment Variables Not Loading
- **Problem**: Settings still using console backend
- **Solution**: Restart your Django server after setting environment variables
- **Check**: Verify `.env` file is in the correct location

### Debug Email Settings

Add this temporary view to check your email configuration:

```python
# In accounts/views.py - FOR DEBUGGING ONLY
from django.http import JsonResponse
from django.conf import settings

def debug_email_config(request):
    """Debug view to check email configuration - REMOVE IN PRODUCTION"""
    if not settings.DEBUG:
        return JsonResponse({'error': 'Only available in debug mode'})
    
    return JsonResponse({
        'EMAIL_BACKEND': settings.EMAIL_BACKEND,
        'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', 'Not set'),
        'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', 'Not set'),
        'EMAIL_USE_TLS': getattr(settings, 'EMAIL_USE_TLS', 'Not set'),
        'EMAIL_HOST_USER': getattr(settings, 'EMAIL_HOST_USER', 'Not set'),
        'DEFAULT_FROM_EMAIL': settings.DEFAULT_FROM_EMAIL,
    })
```

## Security Considerations

1. **Never commit credentials** to version control
2. **Use environment variables** or secure credential management
3. **Use App Passwords** instead of regular passwords when possible
4. **Rotate credentials regularly** in production
5. **Monitor email usage** to detect abuse

## Production Recommendations

For production deployments:

1. **Use a dedicated email service** (SendGrid, AWS SES, Mailgun)
2. **Set up proper SPF/DKIM records** for your domain
3. **Monitor email delivery rates** and bounces
4. **Implement rate limiting** to prevent abuse
5. **Use a dedicated domain** for transactional emails

## Next Steps

1. Choose an email provider from the options above
2. Follow the setup instructions for your chosen provider
3. Set the environment variables
4. Restart your Django server
5. Test user registration with a real email address
6. Verify you receive the verification email

## Support

If you encounter issues:
1. Check the Django console for error messages
2. Verify your email provider's SMTP settings
3. Test with a simple email sending script first
4. Check your email provider's security settings
5. Consult the email provider's documentation for Django integration

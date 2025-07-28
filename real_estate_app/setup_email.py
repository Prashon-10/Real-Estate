#!/usr/bin/env python
"""
Email Setup Helper for Real Estate Application

This script helps you configure real email delivery by updating your .env file.
It provides an interactive setup for common email providers.

Usage:
    python setup_email.py
"""

import os
from pathlib import Path

def get_email_provider_settings(provider):
    """Get SMTP settings for common email providers."""
    
    providers = {
        'gmail': {
            'host': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True,
            'use_ssl': False,
            'instructions': [
                "1. Enable 2-Factor Authentication on your Google account",
                "2. Generate an App Password: https://myaccount.google.com/apppasswords",
                "3. Use the App Password (not your regular password)"
            ]
        },
        'outlook': {
            'host': 'smtp-mail.outlook.com',
            'port': 587,
            'use_tls': True,
            'use_ssl': False,
            'instructions': [
                "1. Use your regular Outlook/Hotmail password",
                "2. If you have 2FA enabled, you may need an App Password"
            ]
        },
        'yahoo': {
            'host': 'smtp.mail.yahoo.com',
            'port': 587,
            'use_tls': True,
            'use_ssl': False,
            'instructions': [
                "1. Enable 'Less secure app access' or use App Password",
                "2. Generate App Password: https://login.yahoo.com/account/security"
            ]
        },
        'custom': {
            'host': '',
            'port': 587,
            'use_tls': True,
            'use_ssl': False,
            'instructions': [
                "1. Contact your email provider for SMTP settings",
                "2. Common ports: 587 (TLS), 465 (SSL), 25 (unsecured)"
            ]
        }
    }
    
    return providers.get(provider, providers['custom'])

def setup_email_configuration():
    """Interactive email configuration setup."""
    
    print("=" * 60)
    print("REAL ESTATE APP - EMAIL SETUP")
    print("=" * 60)
    print()
    
    print("Choose your email provider:")
    print("1. Gmail")
    print("2. Outlook/Hotmail")
    print("3. Yahoo")
    print("4. Custom SMTP")
    print()
    
    choice = input("Enter your choice (1-4): ").strip()
    
    provider_map = {
        '1': 'gmail',
        '2': 'outlook',
        '3': 'yahoo',
        '4': 'custom'
    }
    
    provider = provider_map.get(choice)
    if not provider:
        print("❌ Invalid choice!")
        return False
    
    settings = get_email_provider_settings(provider)
    
    print(f"\n📧 Setting up {provider.upper()} email...")
    print()
    
    # Show instructions
    if settings['instructions']:
        print("Setup Instructions:")
        for instruction in settings['instructions']:
            print(f"   {instruction}")
        print()
    
    # Get user input
    email = input("Enter your email address: ").strip()
    if not email:
        print("❌ Email address is required!")
        return False
    
    password = input("Enter your email password (or App Password): ").strip()
    if not password:
        print("❌ Password is required!")
        return False
    
    # For custom SMTP, get additional settings
    if provider == 'custom':
        host = input("Enter SMTP host: ").strip()
        if not host:
            print("❌ SMTP host is required!")
            return False
        settings['host'] = host
        
        port = input(f"Enter SMTP port (default: {settings['port']}): ").strip()
        if port:
            try:
                settings['port'] = int(port)
            except ValueError:
                print("❌ Invalid port number!")
                return False
        
        use_tls = input("Use TLS? (y/n, default: y): ").strip().lower()
        settings['use_tls'] = use_tls != 'n'
    
    # Create .env content
    env_content = f"""# Email Configuration
# Set DEBUG=False for production email delivery
DEBUG=False
EMAIL_BACKEND=smtp

# SMTP Configuration
EMAIL_HOST={settings['host']}
EMAIL_PORT={settings['port']}
EMAIL_USE_TLS={str(settings['use_tls']).lower()}
EMAIL_USE_SSL={str(settings['use_ssl']).lower()}
EMAIL_HOST_USER={email}
EMAIL_HOST_PASSWORD={password}
DEFAULT_FROM_EMAIL={email}

# Additional settings
EMAIL_SUBJECT_PREFIX=[RealEstate] 
"""
    
    # Write to .env file
    env_path = Path('.env')
    
    if env_path.exists():
        backup = input("\n.env file exists. Create backup? (y/n): ").strip().lower()
        if backup == 'y':
            backup_path = Path('.env.backup')
            env_path.rename(backup_path)
            print(f"✅ Backup created: {backup_path}")
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Email configuration saved to {env_path}")
    print()
    print("🔧 Next steps:")
    print("1. Restart your Django development server")
    print("2. Run: python test_email_config.py")
    print("3. Test user registration with email verification")
    print()
    
    return True

def main():
    """Main function."""
    
    try:
        success = setup_email_configuration()
        
        if success:
            print("✅ Email setup completed successfully!")
            print("You can now test real email delivery.")
        else:
            print("❌ Email setup failed!")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user.")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())

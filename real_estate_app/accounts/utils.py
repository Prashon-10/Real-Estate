import re
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse

# List of commonly accepted email domains
ALLOWED_EMAIL_DOMAINS = {
    # Major email providers
    'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'live.com',
    'icloud.com', 'me.com', 'aol.com', 'protonmail.com', 'tutanota.com',
    
    # Educational domains
    'edu', 'ac.uk', 'edu.au', 'edu.in', 'ac.in', 'university.edu',
    
    # Corporate/Professional domains (common)
    'company.com', 'business.com', 'office.com', 'work.com',
    
    # Government domains
    'gov', 'gov.in', 'gov.uk', 'gov.au', 'mil',
    
    # Other major providers
    'zoho.com', 'fastmail.com', 'yandex.com', 'mail.com'
}

def validate_email_domain(email):
    """
    Validate that the email domain is from a commonly accepted provider
    and not a fake/temporary domain.
    """
    if not email:
        raise ValidationError("Email is required.")
    
    # Basic email format validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        raise ValidationError("Please enter a valid email address.")
    
    # Extract domain
    domain = email.split('@')[1].lower()
    
    # Block obviously fake domains
    fake_patterns = [
        r'\d+\.com$',  # domains like 123.com, 456.com
        r'^test\.',    # test.anything
        r'^fake\.',    # fake.anything
        r'^temp\.',    # temp.anything
        r'\.test$',    # anything.test
        r'\.fake$',    # anything.fake
        r'\.temp$',    # anything.temp
        r'example\.com$',  # example.com
        r'localhost',  # localhost domains
    ]
    
    for pattern in fake_patterns:
        if re.search(pattern, domain):
            raise ValidationError(
                "Please use a valid email address from a recognized email provider."
            )
    
    # Check if domain is in allowed list or has allowed TLD
    domain_parts = domain.split('.')
    tld = domain_parts[-1] if len(domain_parts) > 1 else ''
    
    # Allow if exact domain match or if it's an educational/government domain
    if (domain in ALLOWED_EMAIL_DOMAINS or 
        tld in ['edu', 'gov', 'ac'] or 
        domain.endswith('.edu') or 
        domain.endswith('.gov') or
        domain.endswith('.ac.uk') or
        domain.endswith('.edu.au') or
        domain.endswith('.ac.in')):
        return True
    
    # For other domains, be more restrictive but allow subdomains of major providers
    major_providers = {'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 
                      'live.com', 'icloud.com', 'protonmail.com', 'zoho.com'}
    
    # Check if domain is a major provider or subdomain of major provider
    is_major_provider = (domain in major_providers or 
                        any(domain.endswith('.' + provider) for provider in major_providers))
    
    if not is_major_provider:
        raise ValidationError(
            "Please use an email address from a recognized provider such as "
            "Gmail, Yahoo, Outlook, or your educational/organizational email."
        )
    
    return True

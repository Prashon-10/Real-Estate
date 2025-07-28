"""
Custom email backend for RealEstate Platform
This ensures emails are sent to real inboxes using direct SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class RealEmailBackend(BaseEmailBackend):
    """
    Custom email backend that sends emails using direct SMTP
    This ensures reliable email delivery to real inboxes
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.host = getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com')
        self.port = getattr(settings, 'EMAIL_PORT', 587)
        self.username = getattr(settings, 'EMAIL_HOST_USER', '')
        self.password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        self.use_tls = getattr(settings, 'EMAIL_USE_TLS', True)
        self.use_ssl = getattr(settings, 'EMAIL_USE_SSL', False)
        self.timeout = getattr(settings, 'EMAIL_TIMEOUT', 60)
        
    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number sent.
        """
        if not email_messages:
            return 0
            
        sent_count = 0
        
        try:
            # Create SMTP connection
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout)
            else:
                server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
                
            if self.use_tls and not self.use_ssl:
                server.starttls()
                
            if self.username and self.password:
                server.login(self.username, self.password)
            
            for message in email_messages:
                try:
                    # Convert Django EmailMessage to SMTP format
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = message.subject
                    msg['From'] = message.from_email
                    msg['To'] = ', '.join(message.to)
                    
                    if message.cc:
                        msg['Cc'] = ', '.join(message.cc)
                    if message.bcc:
                        msg['Bcc'] = ', '.join(message.bcc)
                    
                    # Add body
                    if hasattr(message, 'body') and message.body:
                        msg.attach(MIMEText(message.body, 'plain'))
                    
                    # Add HTML alternative if available
                    for content, mimetype in getattr(message, 'alternatives', []):
                        if mimetype == 'text/html':
                            msg.attach(MIMEText(content, 'html'))
                    
                    # Send the email
                    recipients = message.to + message.cc + message.bcc
                    server.send_message(msg, to_addrs=recipients)
                    sent_count += 1
                    
                    logger.info(f"Email sent successfully to {', '.join(message.to)}")
                    
                except Exception as e:
                    logger.error(f"Failed to send email to {', '.join(message.to)}: {e}")
                    if not self.fail_silently:
                        raise
            
            server.quit()
            
        except Exception as e:
            logger.error(f"SMTP connection failed: {e}")
            if not self.fail_silently:
                raise
                
        return sent_count

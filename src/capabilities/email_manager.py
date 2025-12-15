"""Email capabilities for JARVIS assistant."""
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
import json
from pathlib import Path


class EmailManager:
    """Manages email sending and reading capabilities."""
    
    def __init__(self, config_file: str = "data/email_config.json"):
        """
        Initialize email manager.
        
        Args:
            config_file: Path to email configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.is_configured = self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load email configuration from file."""
        try:
            config_path = Path(self.config_file)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading email config: {e}")
        
        # Return default template
        return {
            "smtp_server": "",
            "smtp_port": 587,
            "imap_server": "",
            "imap_port": 993,
            "email": "",
            "password": "",
            "use_tls": True
        }
    
    def _save_config(self):
        """Save email configuration to file."""
        try:
            config_path = Path(self.config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving email config: {e}")
    
    def _validate_config(self) -> bool:
        """Check if email configuration is complete."""
        required = ["smtp_server", "email", "password"]
        return all(self.config.get(key) for key in required)
    
    def configure(self, email_address: str, password: str, 
                  smtp_server: str = "smtp.gmail.com", 
                  imap_server: str = "imap.gmail.com") -> Dict[str, Any]:
        """
        Configure email account.
        
        Args:
            email_address: Your email address
            password: Your email password or app password
            smtp_server: SMTP server address
            imap_server: IMAP server address
            
        Returns:
            Result dictionary
        """
        self.config.update({
            "email": email_address,
            "password": password,
            "smtp_server": smtp_server,
            "imap_server": imap_server,
            "smtp_port": 587,
            "imap_port": 993,
            "use_tls": True
        })
        
        self._save_config()
        self.is_configured = True
        
        return {
            "success": True,
            "message": "Email account configured successfully"
        }
    
    def send_email(self, to: str, subject: str, body: str, 
                   cc: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
            cc: List of CC recipients (optional)
            
        Returns:
            Result dictionary
        """
        if not self.is_configured:
            return {
                "success": False,
                "message": "Email not configured. Please configure your email account first."
            }
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config['email']
            msg['To'] = to
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # Attach body
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            
            if self.config.get('use_tls', True):
                server.starttls()
            
            # Login
            server.login(self.config['email'], self.config['password'])
            
            # Send email
            recipients = [to]
            if cc:
                recipients.extend(cc)
            
            server.send_message(msg)
            server.quit()
            
            return {
                "success": True,
                "message": f"Email sent to {to}"
            }
            
        except smtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "message": "Email authentication failed. Check your password."
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to send email: {str(e)}"
            }
    
    def check_email(self, limit: int = 5) -> Dict[str, Any]:
        """
        Check recent emails.
        
        Args:
            limit: Number of recent emails to retrieve
            
        Returns:
            Result dictionary with email list
        """
        if not self.is_configured:
            return {
                "success": False,
                "message": "Email not configured. Please configure your email account first.",
                "emails": []
            }
        
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.config['imap_server'], self.config['imap_port'])
            
            # Login
            mail.login(self.config['email'], self.config['password'])
            
            # Select inbox
            mail.select('INBOX')
            
            # Search for all emails
            result, data = mail.search(None, 'ALL')
            
            if result != 'OK':
                return {
                    "success": False,
                    "message": "Failed to search emails",
                    "emails": []
                }
            
            # Get email IDs
            email_ids = data[0].split()
            
            # Get most recent emails
            recent_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            recent_ids.reverse()  # Most recent first
            
            emails = []
            for email_id in recent_ids:
                result, data = mail.fetch(email_id, '(RFC822)')
                
                if result != 'OK' or not data or not data[0]:
                    continue
                
                raw_email_data = data[0][1]
                if not isinstance(raw_email_data, bytes):
                    continue
                    
                msg = email.message_from_bytes(raw_email_data)
                
                # Extract email details
                from_addr = msg.get('From', 'Unknown')
                subject = msg.get('Subject', 'No Subject')
                date = msg.get('Date', 'Unknown')
                
                # Get body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain':
                            try:
                                payload = part.get_payload(decode=True)
                                if isinstance(payload, bytes):
                                    body = payload.decode()
                            except:
                                body = "Unable to decode"
                            break
                else:
                    try:
                        payload = msg.get_payload(decode=True)
                        if isinstance(payload, bytes):
                            body = payload.decode()
                    except:
                        body = "Unable to decode"
                
                # Limit body length
                if len(body) > 200:
                    body = body[:200] + "..."
                
                emails.append({
                    "from": from_addr,
                    "subject": subject,
                    "date": date,
                    "preview": body
                })
            
            mail.close()
            mail.logout()
            
            # Create summary message
            if emails:
                count = len(emails)
                summary = f"You have {count} recent email"
                if count > 1:
                    summary += "s"
                summary += f". Latest from {emails[0]['from']}: {emails[0]['subject']}"
            else:
                summary = "No emails found in inbox"
            
            return {
                "success": True,
                "message": summary,
                "emails": emails,
                "count": len(emails)
            }
            
        except imaplib.IMAP4.error:
            return {
                "success": False,
                "message": "Failed to connect to email server. Check your credentials.",
                "emails": []
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error checking email: {str(e)}",
                "emails": []
            }
    
    def read_email(self, index: int = 0) -> Dict[str, Any]:
        """
        Read a specific email by index (0 = most recent).
        
        Args:
            index: Email index (0-based, 0 is most recent)
            
        Returns:
            Result dictionary with email details
        """
        result = self.check_email(limit=index + 1)
        
        if not result['success'] or not result['emails']:
            return {
                "success": False,
                "message": "No email found at that index"
            }
        
        if index >= len(result['emails']):
            return {
                "success": False,
                "message": f"Only {len(result['emails'])} emails available"
            }
        
        email_data = result['emails'][index]
        
        message = f"Email from {email_data['from']}. Subject: {email_data['subject']}. {email_data['preview']}"
        
        return {
            "success": True,
            "message": message,
            "email": email_data
        }
    
    def get_unread_count(self) -> Dict[str, Any]:
        """
        Get count of unread emails.
        
        Returns:
            Result dictionary with unread count
        """
        if not self.is_configured:
            return {
                "success": False,
                "message": "Email not configured",
                "count": 0
            }
        
        try:
            mail = imaplib.IMAP4_SSL(self.config['imap_server'], self.config['imap_port'])
            mail.login(self.config['email'], self.config['password'])
            mail.select('INBOX')
            
            result, data = mail.search(None, 'UNSEEN')
            
            if result != 'OK':
                return {
                    "success": False,
                    "message": "Failed to check unread emails",
                    "count": 0
                }
            
            unread_ids = data[0].split()
            count = len(unread_ids)
            
            mail.close()
            mail.logout()
            
            if count == 0:
                message = "You have no unread emails"
            elif count == 1:
                message = "You have 1 unread email"
            else:
                message = f"You have {count} unread emails"
            
            return {
                "success": True,
                "message": message,
                "count": count
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error checking unread emails: {str(e)}",
                "count": 0
            }

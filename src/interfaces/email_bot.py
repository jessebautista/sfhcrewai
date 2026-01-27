"""
Email bot interface for CrewAI News Manager.
Polls inbox via IMAP, processes commands, and replies via SMTP.
"""
import os
import sys
import time
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.orchestrator import OrchestratorAgent
from src.core.logger import AgentLogger

load_dotenv()


def send_notification_email(to_address, subject, body):
    """
    Global function to send notification emails.
    Can be called from ProposalManager or other modules.
    """
    try:
        email_address = os.environ.get("EMAIL_ADDRESS")
        email_password = os.environ.get("EMAIL_PASSWORD")
        smtp_server = os.environ.get("EMAIL_SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.environ.get("EMAIL_SMTP_PORT", "587"))
        
        if not email_address or not email_password:
            print("Warning: Email credentials not configured")
            return
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = email_address
        msg['To'] = to_address
        msg['Subject'] = subject
        
        # HTML formatted body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2563eb;">CrewAI News Manager</h2>
            <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <pre style="white-space: pre-wrap; word-wrap: break-word; font-family: sans-serif;">
{body}
                </pre>
            </div>
            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
            <p style="color: #6b7280; font-size: 12px;">
                This is an automated notification from CrewAI News Manager.
            </p>
        </body>
        </html>
        """
        
        # Attach both versions
        part_text = MIMEText(body, 'plain')
        part_html = MIMEText(html_body, 'html')
        
        msg.attach(part_text)
        msg.attach(part_html)
        
        # Send
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg)
        
        print(f"✅ Sent notification email to {to_address}")
        
    except Exception as e:
        print(f"❌ Failed to send notification email: {e}")


class EmailBot:
    """Email bot that polls inbox and processes commands via orchestrator."""
    
    def __init__(self):
        # Email configuration
        self.email_address = os.environ.get("EMAIL_ADDRESS")
        self.email_password = os.environ.get("EMAIL_PASSWORD")
        self.imap_server = os.environ.get("EMAIL_IMAP_SERVER", "imap.gmail.com")
        self.imap_port = int(os.environ.get("EMAIL_IMAP_PORT", "993"))
        self.smtp_server = os.environ.get("EMAIL_SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.environ.get("EMAIL_SMTP_PORT", "587"))
        self.poll_interval = int(os.environ.get("EMAIL_POLL_INTERVAL", "60"))
        
        # Validate configuration
        if not self.email_address or not self.email_password:
            raise ValueError("EMAIL_ADDRESS and EMAIL_PASSWORD must be set in .env")
        
        self.logger = AgentLogger()
        print(f"📧 Email Bot initialized for {self.email_address}")
    
    def decode_email_subject(self, subject):
        """Decode email subject from various encodings."""
        if subject is None:
            return ""
        
        decoded_parts = decode_header(subject)
        decoded_subject = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_subject += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_subject += str(part)
        
        return decoded_subject
    
    def extract_email_body(self, msg):
        """Extract plain text body from email message."""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                # Get plain text
                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode('utf-8', errors='ignore')
                            break
                    except Exception as e:
                        print(f"Error decoding text/plain: {e}")
                
                # Fallback to HTML if no plain text
                elif content_type == "text/html" and not body:
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            html_body = payload.decode('utf-8', errors='ignore')
                            # Simple HTML tag removal
                            import re
                            body = re.sub('<[^<]+?>', '', html_body)
                    except Exception as e:
                        print(f"Error decoding text/html: {e}")
        else:
            # Non-multipart email
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='ignore')
            except Exception as e:
                print(f"Error decoding payload: {e}")
        
        return body.strip()
    
    def connect_imap(self):
        """Connect to IMAP server."""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.email_password)
            return mail
        except Exception as e:
            print(f"❌ IMAP connection failed: {e}")
            self.logger.log("EmailBot", "error", f"IMAP connection failed: {e}", status="failure")
            return None
    
    def send_reply(self, to_address, subject, body_text, message_id=None):
        """Send email reply via SMTP."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_address
            msg['To'] = to_address
            msg['Subject'] = f"Re: {subject}" if not subject.startswith("Re:") else subject
            
            # Add threading headers
            if message_id:
                msg['In-Reply-To'] = message_id
                msg['References'] = message_id
            
            # Convert markdown-like output to simple HTML
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #2563eb;">CrewAI News Manager Response</h2>
                <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <pre style="white-space: pre-wrap; word-wrap: break-word; font-family: monospace;">
{body_text}
                    </pre>
                </div>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                <p style="color: #6b7280; font-size: 12px;">
                    This is an automated response from CrewAI News Manager.
                </p>
            </body>
            </html>
            """
            
            # Attach both plain text and HTML versions
            part_text = MIMEText(body_text, 'plain')
            part_html = MIMEText(html_body, 'html')
            
            msg.attach(part_text)
            msg.attach(part_html)
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            print(f"✅ Sent reply to {to_address}")
            self.logger.log("EmailBot", "email_sent", f"Reply sent to {to_address}", 
                          {"subject": subject}, status="success")
            
        except Exception as e:
            print(f"❌ Failed to send reply: {e}")
            self.logger.log("EmailBot", "error", f"Failed to send reply: {e}", status="failure")
    
    def process_email(self, mail, email_id):
        """Process a single email and send response."""
        try:
            # Fetch email data
            status, data = mail.fetch(email_id, '(RFC822)')
            
            if status != 'OK':
                print(f"Failed to fetch email {email_id}")
                return
            
            # Parse email
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            # Extract information
            from_address = msg.get('From')
            subject = self.decode_email_subject(msg.get('Subject'))
            message_id = msg.get('Message-ID')
            body = self.extract_email_body(msg)
            
            print(f"\n📨 New email from: {from_address}")
            print(f"   Subject: {subject}")
            print(f"   Body preview: {body[:100]}...")
            
            # Filter: Only process emails with "COMMAND:" prefix in subject
            if not subject or not subject.upper().startswith("COMMAND:"):
                print(f"⚠️ Skipping email - subject must start with 'COMMAND:'")
                print(f"   Subject was: '{subject}'")
                # Mark as read so we don't keep trying to process it
                try:
                    mail.store(email_id, '+FLAGS', '\\Seen')
                except:
                    pass
                return
            
            # Remove "COMMAND:" prefix from subject for cleaner command
            command = subject[8:].strip()  # Remove "COMMAND:" (8 characters)
            
            if not command.strip():
                print("⚠️ Empty command after COMMAND: prefix, skipping")
                return
            
            # Extract and process attachments
            attachment_context = ""
            try:
                attachments = self.extract_email_attachments(msg)
                
                if attachments:
                    print(f"📎 Processing {len(attachments)} attachment(s)...")
                    
                    from src.core.file_handler import process_files
                    result = process_files(attachments)
                    
                    attachment_context = self.format_attachment_context(result)
                    
                    if result['images']:
                        print(f"✅ Uploaded {len(result['images'])} image(s)")
                    if result['pdf_text']:
                        print(f"✅ Extracted content from files")
                    if result['errors']:
                        for error in result['errors']:
                            print(f"⚠️ {error}")
            
            except Exception as e:
                print(f"⚠️ Error processing attachments: {e}")
            
            self.logger.log("EmailBot", "email_received", 
                          f"Processing email from {from_address}", 
                          {"subject": subject, "command": command})
            
            # Set requester email in context for proposals
            try:
                from src.core.request_context import set_requester_email
                set_requester_email(from_address)
                print(f"   Requester email set: {from_address}")
            except Exception as e:
                print(f"   Warning: Could not set requester context: {e}")
            
            # Run agent
            print(f"🤖 Running agent with command: {command}")
            orchestrator = OrchestratorAgent()
            
            try:
                result = orchestrator.run_mission(command)
                response_text = f"Command: {command}\n\n{result}"
                
                print(f"✅ Agent completed successfully")
                
            except Exception as e:
                print(f"❌ Agent error: {e}")
                response_text = f"Error processing your request: {str(e)}\n\nCommand was: {command}"
                self.logger.log("EmailBot", "error", 
                              f"Agent failed: {e}", 
                              {"command": command}, 
                              status="failure")
            finally:
                # Clear context after processing
                try:
                    from src.core.request_context import clear_request_context
                    clear_request_context()
                except:
                    pass
            
            # Send reply
            self.send_reply(from_address, subject, response_text, message_id)
            
            # Mark email as read so we don't process it again
            try:
                mail.store(email_id, '+FLAGS', '\\Seen')
                print(f"✅ Marked email as read")
            except Exception as e:
                print(f"⚠️ Could not mark email as read: {e}")
            
        except Exception as e:
            print(f"❌ Error processing email: {e}")
            self.logger.log("EmailBot", "error", f"Email processing failed: {e}", status="failure")
    
    def poll_inbox(self):
        """Poll inbox once and process unread emails."""
        mail = self.connect_imap()
        
        if not mail:
            return
        
        try:
            # Select inbox
            mail.select('INBOX')
            
            # Search for unread emails
            status, messages = mail.search(None, 'UNSEEN')
            
            if status != 'OK':
                print("Failed to search inbox")
                return
            
            email_ids = messages[0].split()
            
            if not email_ids:
                print("📭 No new emails")
                return
            
            print(f"📬 Found {len(email_ids)} unread email(s)")
            
            # Process each email
            for email_id in email_ids:
                self.process_email(mail, email_id)
            
        except Exception as e:
            print(f"❌ Error polling inbox: {e}")
            self.logger.log("EmailBot", "error", f"Inbox polling failed: {e}", status="failure")
        
        finally:
            try:
                mail.close()
                mail.logout()
            except:
                pass
    
    def run(self):
        """Main loop: poll inbox at regular intervals."""
        print(f"\n🤖 Email Bot Started!")
        print(f"📧 Monitoring: {self.email_address}")
        print(f"⏱️  Poll interval: {self.poll_interval} seconds")
        print(f"✅ Press Ctrl+C to stop\n")
        
        self.logger.log("EmailBot", "bot_started", 
                       f"Email bot started monitoring {self.email_address}",
                       {"poll_interval": self.poll_interval},
                       status="success")
        
        try:
            while True:
                try:
                    self.poll_inbox()
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(f"❌ Polling error: {e}")
                    # Continue running even if one poll fails
                
                # Wait before next poll
                time.sleep(self.poll_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Email bot stopped by user")
            self.logger.log("EmailBot", "bot_stopped", "Email bot stopped by user")


def main():
    """Entry point for email bot."""
    try:
        bot = EmailBot()
        bot.run()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease ensure EMAIL_ADDRESS and EMAIL_PASSWORD are set in .env")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

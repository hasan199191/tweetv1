import imaplib
import email
import time
import re
import logging
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)

class EmailReader:
    def __init__(self):
        load_dotenv()
        self.email_user = "chefcryptoz@gmail.com"
        self.email_password = "Nuray1965+"
        self.imap_server = "imap.gmail.com"
        logger.info("EmailReader initialized")

    def get_verification_code(self, max_attempts=3):
        logger.info("Attempting to get verification code from email...")
        
        for attempt in range(max_attempts):
            try:
                mail = imaplib.IMAP4_SSL(self.imap_server)
                mail.login(self.email_user, self.email_password)
                logger.info("Successfully logged into Gmail")
                
                mail.select("INBOX")
                
                # Search for recent Twitter verification emails
                search_criteria = '(FROM "info@twitter.com" SUBJECT "verification" UNSEEN)'
                _, messages = mail.search(None, search_criteria)
                
                if not messages[0]:
                    logger.info(f"No verification email found (attempt {attempt + 1})")
                    time.sleep(5)
                    continue
                
                for num in messages[0].split():
                    _, msg = mail.fetch(num, "(RFC822)")
                    email_body = email.message_from_bytes(msg[0][1])
                    
                    for part in email_body.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            codes = re.findall(r'\b\d{6}\b', body)
                            if codes:
                                code = codes[0]
                                logger.info(f"Found verification code: {code}")
                                return code
                                
            except Exception as e:
                logger.error(f"Email reading error: {e}")
            finally:
                try:
                    mail.close()
                    mail.logout()
                except:
                    pass
                    
        logger.error("Failed to get verification code after multiple attempts")
        return None
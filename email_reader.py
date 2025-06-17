import imaplib
import email
<<<<<<< HEAD
import time
import re
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class EmailReader:
    def __init__(self):
        self.email_user = "hasanacikgoz91@gmail.com"  # Your Gmail address
        self.email_password = "Nuray1965+"  # Your Gmail password
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
                    time.sleep(5)  # Wait before next attempt
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
=======
import re
import time
import os
from dotenv import load_dotenv

load_dotenv()

def get_twitter_verification_code(max_attempts=5, delay_between_attempts=10):
    """
    Gmail'den Twitter doğrulama kodunu otomatik olarak al
    """
    print("Email'den Twitter doğrulama kodu alınıyor...")
    
    email_address = os.getenv("TWITTER_EMAIL")
    email_password = os.getenv("EMAIL_PASS")
    
    if not email_address or not email_password:
        print("Email bilgileri bulunamadı!")
        return None
    
    for attempt in range(max_attempts):
        try:
            # IMAP bağlantısı kur
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(email_address, email_password)
            mail.select("inbox")
            
            # Son 5 dakika içinde gelen Twitter maillerini ara
            date = (email.utils.formatdate(
                time.time() - 300
            ))
            result, data = mail.search(None, f'(FROM "info@twitter.com" SINCE "{date}")')
            
            if result != "OK" or not data[0]:
                print(f"Twitter email bulunamadı. Deneme {attempt+1}/{max_attempts}")
                time.sleep(delay_between_attempts)
                continue
                
            # En son emaili al
            latest_email_id = data[0].split()[-1]
            result, email_data = mail.fetch(latest_email_id, "(RFC822)")
            
            if result != "OK":
                print(f"Email içeriği alınamadı. Deneme {attempt+1}/{max_attempts}")
                time.sleep(delay_between_attempts)
                continue
                
            # Email içeriğini parse et
            raw_email = email_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            # Email içeriğini okuma
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain" or content_type == "text/html":
                        try:
                            email_body = part.get_payload(decode=True).decode()
                            # Doğrulama kodunu bul (genellikle 6-8 haneli sayı)
                            code_match = re.search(r'(\d{5,8})', email_body)
                            if code_match:
                                verification_code = code_match.group(1)
                                print(f"Doğrulama kodu bulundu: {verification_code}")
                                mail.close()
                                mail.logout()
                                return verification_code
                        except Exception as e:
                            print(f"Email içerik okuma hatası: {e}")
            else:
                try:
                    email_body = msg.get_payload(decode=True).decode()
                    code_match = re.search(r'(\d{5,8})', email_body)
                    if code_match:
                        verification_code = code_match.group(1)
                        print(f"Doğrulama kodu bulundu: {verification_code}")
                        mail.close()
                        mail.logout()
                        return verification_code
                except Exception as e:
                    print(f"Email içerik okuma hatası: {e}")
            
            mail.close()
            mail.logout()
            print(f"Doğrulama kodu bulunamadı. Deneme {attempt+1}/{max_attempts}")
            time.sleep(delay_between_attempts)
            
        except Exception as e:
            print(f"Email okuma hatası: {e}")
            time.sleep(delay_between_attempts)
    
    print("Maksimum deneme sayısına ulaşıldı. Doğrulama kodu alınamadı.")
    return None
>>>>>>> f4388a922d2200e1f77423b49535a16de066a037

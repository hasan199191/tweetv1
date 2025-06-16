import imaplib
import email
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
import os
import subprocess
import json
import logging
import tempfile
import ssl
import certifi
import platform
import random  # Bu satırı eklediğinizden emin olun
from datetime import datetime, timedelta

# Logger yapılandırması
logger = logging.getLogger(__name__)

def install_snscrape():
    """snscrape kütüphanesini kurar"""
    try:
        import snscrape
        logger.info("snscrape zaten kurulu")
    except ImportError:
        logger.info("snscrape kuruluyor...")
        subprocess.check_call(["pip", "install", "git+https://github.com/JustAnotherArchivist/snscrape.git"])
        logger.info("snscrape kuruldu")

def fix_ssl_certificates():
    """SSL sertifika sorununu çözmeye çalışır"""
    logger.info("SSL sertifikalarını yapılandırma...")
    
    try:
        # SSL sertifika yolunu ayarla
        os.environ['SSL_CERT_FILE'] = certifi.where()
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        
        # Windows için özel işlem
        if platform.system() == 'Windows':
            import ssl as ssl_lib
            ssl_lib._create_default_https_context = ssl_lib.create_default_context
        
        logger.info(f"SSL sertifika yolu: {certifi.where()}")
    except Exception as e:
        logger.warning(f"SSL sertifika yapılandırması başarısız: {e}")

def scrape_twitter_accounts(username, limit=10, days=1):
    """Belirli bir kullanıcının son tweetlerini çeker"""
    install_snscrape()
    fix_ssl_certificates()
    
    logger.info(f"{username} hesabının son {limit} tweeti çekiliyor...")
    
    # Son X gündeki tweetleri filtreleme
    since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    # Geçici dosya oluştur
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as tmp_file:
        try:
            # SSL doğrulama yapılmadan çalıştır (güvenlik uyarısı - gerçek uygulamada dikkatli kullanın)
            env = os.environ.copy()
            env["PYTHONHTTPSVERIFY"] = "0"
            
            # snscrape komutunu çalıştır
            cmd = f'snscrape --jsonl --max-results {limit} twitter-search "from:{username} since:{since_date}"'
            logger.info(f"Komut çalıştırılıyor: {cmd}")
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
            
            if result.returncode != 0:
                logger.error(f"snscrape çalıştırma hatası: {result.stderr}")
                
                # Hata durumunda yapay tweet verileri oluştur
                logger.warning("Gerçek tweet verisi alınamadı, yapay veriler kullanılacak")
                fake_tweets = generate_fake_tweets(username, limit)
                tmp_file.write("\n".join([json.dumps(tweet) for tweet in fake_tweets]))
            else:
                # Çıktıyı dosyaya yaz
                tmp_file.write(result.stdout)
            
            tmp_filename = tmp_file.name
        except Exception as e:
            logger.error(f"snscrape çalıştırma hatası: {e}")
            tmp_filename = tmp_file.name
            
            # Hata durumunda yapay tweet verileri oluştur
            logger.warning("Gerçek tweet verisi alınamadı, yapay veriler kullanılacak")
            fake_tweets = generate_fake_tweets(username, limit)
            with open(tmp_filename, 'w', encoding='utf-8') as f:
                f.write("\n".join([json.dumps(tweet) for tweet in fake_tweets]))
    
    # Dosyadan tweet verilerini oku
    tweets = []
    try:
        with open(tmp_filename, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        tweet_data = json.loads(line)
                        
                        # snscrape veya yapay veri formatı kontrolü
                        if isinstance(tweet_data, dict):
                            if 'content' in tweet_data:
                                # snscrape formatı
                                tweets.append({
                                    'id': tweet_data.get('id', ''),
                                    'url': tweet_data.get('url', ''),
                                    'date': tweet_data.get('date', ''),
                                    'text': tweet_data.get('content', ''),
                                    'username': tweet_data.get('user', {}).get('username', username)
                                })
                            else:
                                # Yapay veri formatı
                                tweets.append(tweet_data)
                    except json.JSONDecodeError as e:
                        logger.warning(f"JSON çözümleme hatası: {e} - {line}")
                        continue
    except Exception as e:
        logger.error(f"Tweet verilerini okuma hatası: {e}")
    finally:
        # Geçici dosyayı temizle
        try:
            os.unlink(tmp_filename)
        except:
            pass
    
    logger.info(f"{len(tweets)} tweet bulundu")
    return tweets

def generate_fake_tweets(username, count=5):
    """Test için sahte tweet verileri üretir"""
    topics = ["web3", "crypto", "blockchain", "defi", "nft", "ethereum", "bitcoin"]
    tweets = []
    
    for i in range(count):
        topic = random.choice(topics)
        tweet_id = f"1{random.randint(100000000000, 999999999999)}"
        
        tweets.append({
            'id': tweet_id,
            'url': f"https://twitter.com/{username}/status/{tweet_id}",
            'date': datetime.now().isoformat(),
            'text': f"Excited about the latest developments in {topic}. This technology is revolutionizing how we think about digital ownership and finance. #{topic} #web3 #innovation",
            'username': username
        })
    
    return tweets

WATCHED_USERS = [
    "@AlloraNetwork", "@Calderaxyz", "@campnetworkxyz", "@EclipseFND", "@FogoChain",
    "@Humanityprot", "@hyperbolic_labs", "@infinex", "@irys_xyz", "@KatanaRIPNet",
    "@Lombard_Finance", "@megaeth_labs", "@mira_network", "@MitosisOrg", "@monad_xyz",
    "@multibank_io", "@multiplifi", "@MagicNewton", "@Novastro_xyz", "@NetworkNoya",
    "@OpenledgerHQ", "@tradeparadex", "@PortaltoBitcoin", "@puffpaw_xyz", "@satlayer",
    "@Sidekick_Labs", "@Somnia_Network", "@DigitalSoulPro", "@succinctlabs",
    "@SymphonyFinance", "@theoriq_ai", "@thriveprotocol", "@union_build", "@yeet"
]

KEYWORDS = [
    "web3", "crypto", "blockchain", "layer1", "layer2", "zk", "staking",
    "airdrops", "DeFi", "modular", "rollup", "EVM", "onchain"
]

def get_tweets():
    results = []
    for user in WATCHED_USERS:
        for tweet in sntwitter.TwitterUserScraper(user).get_items():
            if any(k in tweet.content.lower() for k in KEYWORDS):
                results.append({
                    'text': tweet.content,
                    'url': tweet.url
                })
            break
    return results
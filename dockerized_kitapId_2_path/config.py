import os

class Config:
    """Uygulama konfigürasyonu"""
    
    # Flask konfigürasyonu
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database konfigürasyonu
    DATABASE_CONFIG = {
        'server': os.environ.get('DB_SERVER', 'sql.impark.local'),
        'user': os.environ.get('DB_USER', 'enes.karatas'),
        'password': os.environ.get('DB_PASSWORD', 'Exkaratas2021!*'),
        'database': os.environ.get('DB_DATABASE', 'olcme_db')
    }
    
    # Logging konfigürasyonu
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def init_app(app):
        """Flask app'i başlatırken çalışacak konfigürasyon"""
        import logging
        
        # Logging seviyesini ayarla
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ) 
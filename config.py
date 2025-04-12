import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 기본 설정
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://') or 'postgresql://web_app_db_fyrp_user:tevnID7zCvPlwnbo0Xik5UXsYPRNacbG@dpg-cvt4v2h5pdvs739focv0-a.singapore-postgres.render.com/web_app_db_fyrp'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 세션 설정
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 보안 헤더 설정
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or '8f42a73054b1749b8e58848e5e3c9d4bfb8c9e7d6a5f4c3b2a1'
    
    # 파일 업로드 설정
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Twilio 설정
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    
    # 관리자 설정
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    
    # 서버 설정
    SERVER_NAME = None  # Render.com에서 자동으로 설정됨
    PREFERRED_URL_SCHEME = 'https'
    
    # 이메일 설정 (SMS 대신 이메일 사용)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'postgresql://web_app_db_fyrp_user:tevnID7zCvPlwnbo0Xik5UXsYPRNacbG@dpg-cvt4v2h5pdvs739focv0-a.singapore-postgres.render.com/web_app_db_fyrp'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://web_app_db_fyrp_user:tevnID7zCvPlwnbo0Xik5UXsYPRNacbG@dpg-cvt4v2h5pdvs739focv0-a.singapore-postgres.render.com/web_app_db_fyrp'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

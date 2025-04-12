from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config, Config
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '페이지에 접근하려면 로그인이 필요합니다.'

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 데이터베이스 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    
    # 로그인 매니저 초기화
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '로그인이 필요합니다.'
    login_manager.login_message_category = 'info'
    
    # 사용자 로더 설정
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # 블루프린트 등록
    from app.routes import auth, admin, applicant, worker
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(applicant.bp)
    app.register_blueprint(worker.bp)
    
    # 데이터베이스 마이그레이션 실행
    with app.app_context():
        from flask_migrate import upgrade
        try:
            upgrade()
            print("Database migration completed successfully")
        except Exception as e:
            print(f"Error during database migration: {str(e)}")
    
    return app

# Create app instance
app = create_app()

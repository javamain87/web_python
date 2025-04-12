from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '페이지에 접근하려면 로그인이 필요합니다.'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models import User
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Import and register blueprints
    from app.routes import auth, admin, worker, applicant
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(worker.bp)
    app.register_blueprint(applicant.bp)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app

# Create app instance
app = create_app()

from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    user_type = db.Column(db.String(20))
    account_number = db.Column(db.String(20))
    phone_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applicant_links = db.relationship('Link', foreign_keys='Link.applicant_id', backref='applicant', lazy='dynamic')
    worker_links = db.relationship('Link', foreign_keys='Link.worker_id', backref='worker', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class WorkLog(db.Model):
    __tablename__ = 'work_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('links.id'), nullable=False)
    work_date = db.Column(db.Date, nullable=True)  # 작업 날짜
    start_time = db.Column(db.Time, nullable=True)  # 시작 시간
    end_time = db.Column(db.Time, nullable=True)  # 종료 시간
    break_time = db.Column(db.Integer)  # Break time in minutes
    description = db.Column(db.Text)
    content = db.Column(db.Text)  # 로그 내용
    action = db.Column(db.String(50))  # 작업 유형
    details = db.Column(db.Text)  # 상세 내용
    worker_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 작업자 ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 
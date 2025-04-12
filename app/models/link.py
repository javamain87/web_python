from datetime import datetime
from .. import db

class Link(db.Model):
    __tablename__ = 'links'
    
    id = db.Column(db.Integer, primary_key=True)
    link_code = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))
    link_type = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    applicant_name = db.Column(db.String(100))
    applicant_phone = db.Column(db.String(20))
    worker_name = db.Column(db.String(100))
    worker_phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    worker_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    admin = db.relationship('User', foreign_keys=[admin_id], backref=db.backref('admin_links', lazy='dynamic'))
    applicant = db.relationship('User', foreign_keys=[applicant_id], backref=db.backref('applicant_links', lazy='dynamic'))
    worker = db.relationship('User', foreign_keys=[worker_id], backref=db.backref('worker_links', lazy='dynamic'))
    
    # Work Logs
    work_logs = db.relationship('WorkLog', backref='link', lazy='dynamic')
    
    def __repr__(self):
        return f'<Link {self.link_code}>'

    def check_password(self, password):
        return self.password == password
        
    def set_password(self, password):
        self.password = password 
from datetime import datetime
from .. import db

class WorkLog(db.Model):
    __tablename__ = 'work_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    work_date = db.Column(db.Date, nullable=False)  # 작업 날짜
    description = db.Column(db.Text)  # 작업 내용
    start_time = db.Column(db.Time, nullable=True)  # 시작 시간
    end_time = db.Column(db.Time, nullable=True)    # 종료 시간
    action = db.Column(db.String(64))  # create, update, delete 등의 액션
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    link_id = db.Column(db.Integer, db.ForeignKey('links.id'))
    worker_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<WorkLog {self.id}>' 
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app.models import User, Link, WorkLog
from app import db
import secrets
from datetime import datetime
from twilio.rest import Client
import os
import socket

# Twilio 계정 정보
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# 서버 IP 주소 가져오기
def get_server_ip():
    try:
        # 소켓을 생성하여 외부 서버에 연결
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google DNS 서버에 연결
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except:
        return 'localhost'

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_administrator():
            flash('관리자 권한이 필요합니다.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def send_sms(to_number, message):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )
        return True
    except Exception as e:
        print(f"SMS 전송 실패: {str(e)}")
        return False

@bp.route('/')
@login_required
@admin_required
def index():
    links = Link.query.all()
    return render_template('admin/index.html', links=links)

@bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@bp.route('/links')
@login_required
@admin_required
def links():
    links = Link.query.all()
    return render_template('admin/links.html', links=links)

@bp.route('/links/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_link():
    if request.method == 'GET':
        return render_template('admin/create_link.html')
        
    if request.method == 'POST':
        try:
            # Get form data
            applicant_name = request.form.get('applicant_name')
            worker_name = request.form.get('worker_name')
            applicant_phone = request.form.get('applicant_phone')
            worker_phone = request.form.get('worker_phone')
            applicant_account = request.form.get('applicant_account')
            worker_account = request.form.get('worker_account')
            
            # Create users if they don't exist
            applicant = User.query.filter_by(username=applicant_name).first()
            if not applicant:
                applicant = User(
                    email=f"{applicant_name.replace(' ', '_').lower()}@example.com",
                    username=applicant_name,
                    phone_number=applicant_phone,
                    account_number=applicant_account if applicant_account else None,
                    user_type='applicant'
                )
                applicant.set_password('default123')  # 기본 비밀번호 설정
                db.session.add(applicant)
            
            worker = User.query.filter_by(username=worker_name).first()
            if not worker:
                worker = User(
                    email=f"{worker_name.replace(' ', '_').lower()}@example.com",
                    username=worker_name,
                    phone_number=worker_phone,
                    account_number=worker_account if worker_account else None,
                    user_type='worker'
                )
                worker.set_password('default123')  # 기본 비밀번호 설정
                db.session.add(worker)
            
            # Create link
            link_code = secrets.token_urlsafe(16)
            link_password = request.form.get('link_password')
            
            link = Link(
                link_code=link_code,
                password=link_password,  # 직접 password 설정
                link_type='work',
                applicant=applicant,
                worker=worker,
                admin_id=current_user.id,
                applicant_name=applicant_name,
                applicant_phone=applicant_phone,
                worker_name=worker_name,
                worker_phone=worker_phone
            )
            db.session.add(link)
            
            # Create work log
            log = WorkLog(
                link=link,
                work_date=datetime.now().date(),
                content=f'Link created for {applicant_name} and {worker_name}',
                action='create',
                details=f'Created by {current_user.username}',
                worker_id=worker.id
            )
            db.session.add(log)
            
            db.session.commit()
            
            # TODO: Send SMS to applicant and worker
            
            flash('링크가 성공적으로 생성되었습니다.', 'success')
            return redirect(url_for('admin.links'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'에러가 발생했습니다: {str(e)}', 'danger')
            return render_template('admin/create_link.html')

@bp.route('/links/<int:link_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_link(link_id):
    link = Link.query.get_or_404(link_id)
    
    if request.method == 'POST':
        try:
            # Update user information
            link.applicant.username = request.form.get('applicant_name')
            link.worker.username = request.form.get('worker_name')
            link.applicant.phone_number = request.form.get('applicant_phone')
            link.worker.phone_number = request.form.get('worker_phone')
            link.applicant.account_number = request.form.get('applicant_account')
            link.worker.account_number = request.form.get('worker_account')
            
            # Create work log
            log = WorkLog(
                link=link,
                work_date=datetime.now().date(),
                content='Link information updated',
                action='update',
                details=f'Updated by {current_user.username}',
                worker_id=link.worker_id
            )
            db.session.add(log)
            
            db.session.commit()
            flash('링크 정보가 성공적으로 수정되었습니다.', 'success')
            return redirect(url_for('admin.links'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'에러가 발생했습니다: {str(e)}', 'danger')
            return render_template('admin/edit_link.html', link=link)
    
    return render_template('admin/edit_link.html', link=link)

@bp.route('/links/<int:link_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    
    try:
        # Create work log
        log = WorkLog(
            link=link,
            work_date=datetime.now().date(),
            content='Link deleted',
            action='delete',
            details=f'Deleted by {current_user.username}',
            worker_id=link.worker_id
        )
        db.session.add(log)
        
        # Delete link
        db.session.delete(link)
        db.session.commit()
        
        flash('링크가 성공적으로 삭제되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'에러가 발생했습니다: {str(e)}', 'danger')
    
    return redirect(url_for('admin.links'))

@bp.route('/links/<int:link_id>/send', methods=['GET'])
@login_required
@admin_required
def send_link(link_id):
    link = Link.query.get_or_404(link_id)
    
    # 신청자용 링크 생성
    applicant_link = url_for('auth.register_link', link_code=link.link_code, _external=True)
    applicant_message = f"[아르바이트 작업일지]\n신청자 링크: {applicant_link}\n비밀번호: {link.password}"
    
    # 작업자용 링크 생성
    worker_link = url_for('auth.register_link', link_code=link.link_code, _external=True)
    worker_message = f"[아르바이트 작업일지]\n작업자 링크: {worker_link}\n비밀번호: {link.password}"
    
    # SMS 전송
    applicant_sent = send_sms(link.applicant.phone_number, applicant_message)
    worker_sent = send_sms(link.worker.phone_number, worker_message)
    
    if applicant_sent and worker_sent:
        flash('SMS가 성공적으로 전송되었습니다.', 'success')
    else:
        flash('SMS 전송 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('admin.links'))

@bp.route('/link/<link_code>')
def view_link(link_code):
    link = Link.query.filter_by(link_code=link_code).first_or_404()
    
    # 작업 로그 가져오기 (최신순으로 정렬)
    work_logs = WorkLog.query.filter_by(link_id=link.id).order_by(WorkLog.created_at.desc()).all()
    
    return render_template('admin/view_link.html', 
                         link=link,
                         work_logs=work_logs) 
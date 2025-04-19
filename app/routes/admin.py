from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app.models import User, Link, WorkLog
from app import db
import secrets
from datetime import datetime, timedelta
from twilio.rest import Client
import os
import socket
from app.forms import LinkForm
from sqlalchemy import func

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

@bp.route('/create_link', methods=['GET', 'POST'])
@login_required
@admin_required
def create_link():
    if request.method == 'POST':
        # 폼 데이터 가져오기
        applicant_name = request.form.get('applicant_name')
        applicant_phone = request.form.get('applicant_phone')
        worker_name = request.form.get('worker_name')
        worker_phone = request.form.get('worker_phone')
        password = request.form.get('password')
        is_active = request.form.get('is_active') == 'on'
        
        # 필수 필드 확인
        if not all([applicant_name, applicant_phone, worker_name, worker_phone, password]):
            flash('모든 필드를 입력해주세요.', 'error')
            return render_template('admin/create_link.html')
        
        # 링크 코드 생성
        link_code = secrets.token_urlsafe(16)
        
        # 링크 생성
        link = Link(
            link_code=link_code,
            applicant_name=applicant_name,
            applicant_phone=applicant_phone,
            worker_name=worker_name,
            worker_phone=worker_phone,
            password=password,
            is_active=is_active,
            link_type='work',
            admin_id=current_user.id
        )
        
        try:
            db.session.add(link)
            db.session.commit()
            
            # 링크 URL 생성
            link_url = url_for('main.view_link', link_code=link_code, _external=True)
            
            flash(f'링크가 생성되었습니다.\n링크: {link_url}\n비밀번호: {password}', 'success')
            return redirect(url_for('admin.links'))
        except Exception as e:
            db.session.rollback()
            flash(f'링크 생성 중 오류가 발생했습니다: {str(e)}', 'error')
            return render_template('admin/create_link.html')
    
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
@login_required
@admin_required
def view_link(link_code):
    link = Link.query.filter_by(link_code=link_code).first_or_404()
    
    # 작업 로그 가져오기 (최신순으로 정렬)
    work_logs = WorkLog.query.filter_by(link_id=link.id).order_by(WorkLog.created_at.desc()).all()
    
    # 신청자와 작업자 정보 가져오기
    applicant = User.query.get(link.applicant_id)
    worker = User.query.get(link.worker_id)
    
    return render_template('admin/view_link.html', 
                         link=link,
                         work_logs=work_logs,
                         applicant=applicant,
                         worker=worker)

@bp.route('/public/link/<link_code>')
def public_view_link(link_code):
    link = Link.query.filter_by(link_code=link_code).first_or_404()
    
    if not link.is_active:
        flash('이 링크는 더 이상 사용할 수 없습니다.', 'error')
        return redirect(url_for('main.index'))
    
    # 작업 로그 가져오기 (최신순으로 정렬)
    work_logs = WorkLog.query.filter_by(link_id=link.id).order_by(WorkLog.created_at.desc()).all()
    
    # 신청자와 작업자 정보 가져오기
    applicant = User.query.get(link.applicant_id)
    worker = User.query.get(link.worker_id)
    
    return render_template('admin/view_link.html', 
                         link=link,
                         work_logs=work_logs,
                         applicant=applicant,
                         worker=worker,
                         is_public=True)

@bp.route('/api/visitor_stats')
@login_required
@admin_required
def visitor_stats():
    # 최근 7일간의 방문자 통계
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)
    
    # 일별 방문자 수 조회
    stats = db.session.query(
        func.date(WorkLog.created_at).label('date'),
        func.count(WorkLog.id).label('count')
    ).filter(
        WorkLog.created_at >= start_date,
        WorkLog.created_at <= end_date
    ).group_by(
        func.date(WorkLog.created_at)
    ).all()
    
    # 결과를 딕셔너리로 변환
    result = {
        'labels': [],
        'data': []
    }
    
    # 모든 날짜에 대해 데이터 생성
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        result['labels'].append(date_str)
        
        # 해당 날짜의 방문자 수 찾기
        count = next((stat.count for stat in stats if stat.date == current_date), 0)
        result['data'].append(count)
        
        current_date += timedelta(days=1)
    
    return jsonify(result)

@bp.route('/api/today_visitors')
@login_required
@admin_required
def today_visitors():
    # 오늘의 방문자 목록
    today = datetime.now().date()
    
    visitors = db.session.query(
        WorkLog.id,
        User.username,
        User.phone_number,
        User.account_number
    ).join(
        User, WorkLog.worker_id == User.id
    ).filter(
        func.date(WorkLog.created_at) == today
    ).order_by(
        WorkLog.created_at.desc()
    ).all()
    
    # 결과를 리스트로 변환
    result = []
    for i, visitor in enumerate(visitors, 1):
        result.append({
            'id': i,
            'name': visitor.username,
            'phone': visitor.phone_number,
            'account': visitor.account_number
        })
    
    return jsonify(result) 
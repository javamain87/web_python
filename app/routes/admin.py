from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from app.models import User, Link, WorkLog, AccessLog
from app import db
import secrets
from datetime import datetime, timedelta
from twilio.rest import Client
import os
import socket
from app.forms import LinkForm
from sqlalchemy import func
import string

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
    try:
        # Get all links
        links = Link.query.order_by(Link.created_at.desc()).all()
        
        # Get today's visitors
        today = datetime.utcnow().date()
        visitors = WorkLog.query.filter(
            func.date(WorkLog.created_at) == today
        ).distinct(WorkLog.worker_id).count()
        
        # Get total work logs
        total_work_logs = WorkLog.query.count()
        
        # Get recent access logs
        recent_logs = AccessLog.query.order_by(AccessLog.created_at.desc()).limit(10).all()
        
        return render_template('admin/index.html',
                             links=links,
                             visitors=visitors,
                             total_work_logs=total_work_logs,
                             recent_logs=recent_logs)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        current_app.logger.error(f'Error loading admin dashboard: {str(e)}')
        return render_template('admin/index.html',
                             links=[],
                             visitors=0,
                             total_work_logs=0,
                             recent_logs=[])

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
    form = LinkForm()
    if form.validate_on_submit():
        try:
            # Generate a unique link code
            while True:
                link_code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
                if not Link.query.filter_by(code=link_code).first():
                    break

            # Create new link
            link = Link(
                code=link_code,
                name=form.name.data,
                phone_number=form.phone_number.data,
                created_by=current_user.id,
                expires_at=datetime.utcnow() + timedelta(days=1)
            )
            db.session.add(link)
            db.session.commit()

            # Log the link creation
            access_log = AccessLog(
                user_id=current_user.id,
                action='create_link',
                details=f'Created link: {link_code}'
            )
            db.session.add(access_log)
            db.session.commit()

            flash('Link created successfully!', 'success')
            return redirect(url_for('admin.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating link: {str(e)}', 'danger')
            current_app.logger.error(f'Error creating link: {str(e)}')
    return render_template('admin/create_link.html', form=form)

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

@bp.route('/delete_link/<int:link_id>', methods=['POST'])
@login_required
@admin_required
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    try:
        # Log the link deletion
        access_log = AccessLog(
            user_id=current_user.id,
            action='delete_link',
            details=f'Deleted link: {link.code}'
        )
        db.session.add(access_log)
        
        db.session.delete(link)
        db.session.commit()
        flash('Link deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting link: {str(e)}', 'danger')
        current_app.logger.error(f'Error deleting link: {str(e)}')
    return redirect(url_for('admin.index'))

@bp.route('/links/<int:link_id>/send', methods=['GET'])
@login_required
@admin_required
def send_link(link_id):
    link = Link.query.get_or_404(link_id)
    
    # 신청자용 링크 생성
    applicant_link = url_for('auth.register_link', link_code=link.link_code, _external=True)
    applicant_message = f"[Escrow Management]\n신청자 링크: {applicant_link}\n비밀번호: {link.password}"
    
    # 작업자용 링크 생성
    worker_link = url_for('auth.register_link', link_code=link.link_code, _external=True)
    worker_message = f"[Escrow Management]\n작업자 링크: {worker_link}\n비밀번호: {link.password}"
    
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
    link = Link.query.filter_by(code=link_code).first_or_404()
    return render_template('admin/view_link.html', link=link)

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
    try:
        # Get visitor stats for the last 7 days
        stats = []
        for i in range(6, -1, -1):
            date = datetime.utcnow().date() - timedelta(days=i)
            count = WorkLog.query.filter(
                func.date(WorkLog.created_at) == date
            ).distinct(WorkLog.worker_id).count()
            stats.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })
        return {'stats': stats}
    except Exception as e:
        current_app.logger.error(f'Error getting visitor stats: {str(e)}')
        return {'error': str(e)}, 500

@bp.route('/api/today_visitors')
@login_required
@admin_required
def today_visitors():
    try:
        today = datetime.utcnow().date()
        visitors = WorkLog.query.filter(
            func.date(WorkLog.created_at) == today
        ).distinct(WorkLog.worker_id).all()
        
        visitor_list = []
        for visitor in visitors:
            user = User.query.get(visitor.worker_id)
            if user:
                visitor_list.append({
                    'name': user.username,
                    'phone': user.phone_number,
                    'time': visitor.created_at.strftime('%H:%M')
                })
        return {'visitors': visitor_list}
    except Exception as e:
        current_app.logger.error(f'Error getting today\'s visitors: {str(e)}')
        return {'error': str(e)}, 500 
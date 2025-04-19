from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Link, WorkLog, AccessLog
from app import db
from functools import wraps
from datetime import datetime

bp = Blueprint('worker', __name__, url_prefix='/worker')

def worker_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.register_link'))
        if current_user.user_type != 'worker':
            flash('Only workers can access this page.', 'error')
            return redirect(url_for('auth.register_link'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@worker_required
def index():
    try:
        # Get all links where current user is the worker
        links = Link.query.filter_by(worker_id=current_user.id).all()
        return render_template('worker/index.html', links=links)
    except Exception as e:
        flash('Error loading dashboard.', 'error')
        return redirect(url_for('auth.register_link'))

@bp.route('/link/<link_code>')
@worker_required
def view_link(link_code):
    link = Link.query.filter_by(link_code=link_code).first_or_404()
    
    if not link.is_active:
        flash('This link is no longer available.', 'error')
        return redirect(url_for('auth.register_link'))
    
    # 작업 로그 가져오기 (최신순으로 정렬)
    work_logs = WorkLog.query.filter_by(link_id=link.id).order_by(WorkLog.created_at.desc()).all()
    
    return render_template('worker/view_link.html', 
                         link=link,
                         work_logs=work_logs)

@bp.route('/link/<link_code>/update_account', methods=['POST'])
@worker_required
def update_account(link_code):
    link = Link.query.filter_by(link_code=link_code).first_or_404()
    
    if not link.is_active:
        flash('This link is no longer available.', 'error')
        return redirect(url_for('auth.register_link'))
    
    account_number = request.form.get('account_number')
    if not account_number:
        flash('Please enter your account number.', 'error')
        return redirect(url_for('worker.view_link', link_code=link_code))
    
    # 계좌번호 업데이트
    link.worker.account_number = account_number
    db.session.commit()
    
    flash('Account number has been updated.', 'success')
    return redirect(url_for('worker.view_link', link_code=link_code))

@bp.route('/link/<link_code>/create_work_log', methods=['POST'])
@worker_required
def create_work_log(link_code):
    link = Link.query.filter_by(link_code=link_code).first_or_404()
    if not link.is_active:
        flash('This link is no longer available.', 'error')
        return redirect(url_for('auth.register_link'))

    work_date = request.form.get('work_date')
    description = request.form.get('description')

    if not work_date or not description:
        flash('Please enter both work date and description.', 'error')
        return redirect(url_for('worker.view_link', link_code=link_code))

    try:
        work_date = datetime.strptime(work_date, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format.', 'error')
        return redirect(url_for('worker.view_link', link_code=link_code))

    work_log = WorkLog(
        link_id=link.id,
        work_date=work_date,
        description=description,
        worker_id=current_user.id,
        action='create'
    )
    db.session.add(work_log)

    # 접속 로그 기록
    access_log = AccessLog(
        user_id=current_user.id,
        action='work_log_create',
        details=f'Created work log for date {work_date}'
    )
    db.session.add(access_log)
    
    db.session.commit()

    flash('Work log has been saved.', 'success')
    return redirect(url_for('worker.view_link', link_code=link_code)) 
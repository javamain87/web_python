from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Link, WorkLog
from app import db
from functools import wraps
from datetime import datetime

bp = Blueprint('worker', __name__, url_prefix='/worker')

def worker_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@worker_required
def index():
    # Get all links where current user is the worker
    links = Link.query.filter_by(worker_id=current_user.id).all()
    return render_template('worker/index.html', links=links)

@bp.route('/link/<link_code>')
@login_required
@worker_required
def view_link(link_code):
    link = Link.query.filter_by(link_code=link_code).first_or_404()
    
    if not link.is_active:
        flash('이 링크는 더 이상 사용할 수 없습니다.', 'error')
        return redirect(url_for('main.index'))
    
    # 작업 로그 가져오기 (최신순으로 정렬)
    work_logs = WorkLog.query.filter_by(link_id=link.id).order_by(WorkLog.created_at.desc()).all()
    
    return render_template('worker/view_link.html', 
                         link=link,
                         work_logs=work_logs)

@bp.route('/link/<link_code>/update_account', methods=['POST'])
@login_required
@worker_required
def update_account(link_code):
    link = Link.query.filter_by(link_code=link_code).first_or_404()
    
    if not link.is_active:
        flash('이 링크는 더 이상 사용할 수 없습니다.', 'error')
        return redirect(url_for('auth.login'))
    
    account_number = request.form.get('account_number')
    if not account_number:
        flash('계좌번호를 입력해주세요.', 'error')
        return redirect(url_for('worker.view_link', link_code=link_code))
    
    # 계좌번호 업데이트
    link.worker.account_number = account_number
    db.session.commit()
    
    flash('계좌번호가 업데이트되었습니다.', 'success')
    return redirect(url_for('worker.view_link', link_code=link_code))

@bp.route('/link/<link_code>/create_work_log', methods=['POST'])
@login_required
@worker_required
def create_work_log(link_code):
    link = Link.query.filter_by(link_code=link_code).first_or_404()
    if not link.is_active:
        flash('이 링크는 더 이상 사용할 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    work_date = request.form.get('work_date')
    description = request.form.get('description')

    if not work_date or not description:
        flash('작업 날짜와 작업 내용을 모두 입력해주세요.', 'error')
        return redirect(url_for('worker.view_link', link_code=link_code))

    try:
        work_date = datetime.strptime(work_date, '%Y-%m-%d').date()
    except ValueError:
        flash('올바른 날짜 형식이 아닙니다.', 'error')
        return redirect(url_for('worker.view_link', link_code=link_code))

    work_log = WorkLog(
        link_id=link.id,
        work_date=work_date,
        description=description,
        worker_id=current_user.id
    )
    db.session.add(work_log)
    db.session.commit()

    flash('작업 내용이 저장되었습니다.', 'success')
    return redirect(url_for('worker.view_link', link_code=link_code)) 
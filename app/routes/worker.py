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
def view_link(link_code):
    link = Link.query.filter_by(link_code=link_code).first_or_404()
    
    # 링크가 활성 상태인지 확인
    if not link.is_active:
        flash('이 링크는 더 이상 사용할 수 없습니다.', 'error')
        return redirect(url_for('auth.login'))
    
    # 작업자 정보 확인
    if not link.worker:
        flash('작업자 정보가 없습니다.', 'error')
        return redirect(url_for('auth.login'))
    
    # 작업 로그 가져오기 (최신순으로 정렬)
    work_logs = WorkLog.query.filter_by(link_id=link.id).order_by(WorkLog.created_at.desc()).all()
    
    return render_template('worker/view_link.html', 
                         link=link,
                         work_logs=work_logs)

@bp.route('/link/<link_code>/update', methods=['POST'])
def update_work_log(link_code):
    link = Link.query.filter_by(link_code=link_code).first_or_404()
    
    if not link.is_active:
        flash('이 링크는 더 이상 사용할 수 없습니다.', 'error')
        return redirect(url_for('auth.login'))
    
    content = request.form.get('content')
    if not content:
        flash('작업 내용을 입력해주세요.', 'error')
        return redirect(url_for('worker.view_link', link_code=link_code))
    
    # 새 작업 로그 생성
    work_log = WorkLog(
        link_id=link.id,
        content=content,
        created_at=datetime.utcnow()
    )
    
    db.session.add(work_log)
    db.session.commit()
    
    flash('작업 내용이 업데이트되었습니다.', 'success')
    return redirect(url_for('worker.view_link', link_code=link_code))

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

@bp.route('/link/<link_code>/add_work_log', methods=['POST'])
@login_required
@worker_required
def add_work_log(link_code):
    link = Link.query.filter_by(link_code=link_code).first_or_404()
    
    if not link.is_active:
        flash('이 링크는 더 이상 사용할 수 없습니다.', 'error')
        return redirect(url_for('auth.login'))
    
    description = request.form.get('description')
    
    if not description:
        flash('작업 내용을 입력해주세요.', 'error')
        return redirect(url_for('worker.view_link', link_code=link_code))
    
    try:
        work_log = WorkLog(
            link_id=link.id,
            description=description,
            created_at=datetime.utcnow()
        )
        db.session.add(work_log)
        db.session.commit()
        flash('작업 내용이 저장되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('작업 내용 저장 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('worker.view_link', link_code=link_code)) 
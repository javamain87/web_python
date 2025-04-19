from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Link, User, WorkLog
from app import db
from functools import wraps

bp = Blueprint('applicant', __name__, url_prefix='/applicant')

def applicant_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.register_link'))
        if current_user.user_type != 'applicant':
            flash('Only applicants can access this page.', 'error')
            return redirect(url_for('auth.register_link'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@applicant_required
def index():
    try:
        # Get all links where current user is the applicant
        links = Link.query.filter_by(applicant_id=current_user.id).all()
        return render_template('applicant/index.html', links=links)
    except Exception as e:
        flash('Error loading dashboard.', 'error')
        return redirect(url_for('auth.register_link'))

@bp.route('/link/<link_code>')
@applicant_required
def view_link(link_code):
    link = Link.query.filter_by(link_code=link_code).first_or_404()
    
    # 링크가 활성 상태인지 확인
    if not link.is_active:
        flash('This link is no longer available.', 'error')
        return redirect(url_for('auth.register_link'))
    
    # 신청자 정보 확인
    if not link.applicant:
        flash('Applicant information not found.', 'error')
        return redirect(url_for('auth.register_link'))
    
    # 작업 로그 가져오기
    work_logs = WorkLog.query.filter_by(link_id=link.id).order_by(WorkLog.created_at.desc()).all()
    
    return render_template('applicant/view_link.html', 
                         link=link,
                         work_logs=work_logs)

@bp.route('/link/<link_code>/update_account', methods=['POST'])
@applicant_required
def update_account(link_code):
    link = Link.query.filter_by(link_code=link_code).first_or_404()
    
    if not link.is_active:
        flash('This link is no longer available.', 'error')
        return redirect(url_for('auth.register_link'))
    
    account_number = request.form.get('account_number')
    if not account_number:
        flash('Please enter your account number.', 'error')
        return redirect(url_for('applicant.view_link', link_code=link_code))
    
    # 계좌번호 업데이트
    link.applicant.account_number = account_number
    db.session.commit()
    
    flash('Account number has been updated.', 'success')
    return redirect(url_for('applicant.view_link', link_code=link_code)) 
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user
from app.models import User, Link, UserType
from app import db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('main/index.html')

@bp.route('/link/<link_code>')
def view_link(link_code):
    # 링크 존재 여부 확인
    link = Link.query.filter_by(link_code=link_code).first_or_404()
    
    if not link.is_active:
        flash('이 링크는 더 이상 사용할 수 없습니다.', 'error')
        return redirect(url_for('main.index'))
    
    # 로그인하지 않은 경우 로그인 페이지로 리다이렉트
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    # 관리자인 경우
    if current_user.is_administrator():
        return redirect(url_for('admin.view_link', link_code=link_code))
    
    # 신청자인 경우
    if current_user.user_type == 'applicant' and current_user.id == link.applicant_id:
        return redirect(url_for('applicant.view_link', link_code=link_code))
    
    # 작업자인 경우
    if current_user.user_type == 'worker' and current_user.id == link.worker_id:
        return redirect(url_for('worker.view_link', link_code=link_code))
    
    # 권한이 없는 경우
    flash('이 링크에 접근할 권한이 없습니다.', 'error')
    return redirect(url_for('main.index')) 
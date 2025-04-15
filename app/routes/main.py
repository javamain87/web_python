from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import current_user, login_user
from app.models import User, Link, UserType
from app import db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('main/index.html')

@bp.route('/link/<link_code>', methods=['GET', 'POST'])
def view_link(link_code):
    # 링크 존재 여부 확인
    link = Link.query.filter_by(link_code=link_code).first_or_404()
    
    if not link.is_active:
        flash('이 링크는 더 이상 사용할 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # 이미 인증된 경우
    if current_user.is_authenticated:
        if current_user.is_administrator():
            return redirect(url_for('admin.view_link', link_code=link_code))
        elif current_user.user_type == 'applicant' and current_user.id == link.applicant_id:
            return redirect(url_for('applicant.view_link', link_code=link_code))
        elif current_user.user_type == 'worker' and current_user.id == link.worker_id:
            return redirect(url_for('worker.view_link', link_code=link_code))
    
    # POST 요청 처리 (인증)
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        # 신청자 확인
        if name == link.applicant_name and phone == link.applicant_phone and password == link.password:
            user = User.query.get(link.applicant_id)
            login_user(user)
            return redirect(url_for('applicant.view_link', link_code=link_code))
        
        # 작업자 확인
        if name == link.worker_name and phone == link.worker_phone and password == link.password:
            user = User.query.get(link.worker_id)
            login_user(user)
            return redirect(url_for('worker.view_link', link_code=link_code))
        
        flash('입력하신 정보가 올바르지 않습니다.', 'error')
    
    # GET 요청 - 인증 폼 표시
    return render_template('main/link_auth.html', link_code=link_code) 
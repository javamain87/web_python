from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Link, UserType
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.index'))
        elif current_user.user_type == 'applicant':
            return redirect(url_for('applicant.index'))
        else:
            return redirect(url_for('worker.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')  # 이메일 대신 이름으로 변경
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()  # 이메일 대신 이름으로 검색
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin.index'))
            elif user.user_type == 'applicant':
                return redirect(url_for('applicant.index'))
            else:
                return redirect(url_for('worker.index'))
        else:
            flash('이름 또는 비밀번호가 올바르지 않습니다.', 'error')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/register_link/<link_code>', methods=['GET', 'POST'])
def register_link(link_code):
    link = Link.query.filter_by(link_code=link_code).first_or_404()
    
    if not link.is_active:
        flash('이 링크는 더 이상 사용할 수 없습니다.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')  # 전화번호 추가
        password = request.form.get('password')
        
        if not name or not password or not phone:  # 전화번호 체크 추가
            flash('이름, 전화번호, 비밀번호를 모두 입력해주세요.', 'error')
            return render_template('auth/register_link.html', link=link)
        
        # 이름과 전화번호, 비밀번호 검증
        if ((name == link.applicant_name and phone == link.applicant_phone) or 
            (name == link.worker_name and phone == link.worker_phone)) and link.check_password(password):
            # 해당 사용자 찾기
            user = None
            if name == link.applicant_name and phone == link.applicant_phone:
                user = link.applicant
            elif name == link.worker_name and phone == link.worker_phone:
                user = link.worker
            
            if user:
                login_user(user)  # 사용자 로그인
                if name == link.applicant_name:
                    return redirect(url_for('applicant.view_link', link_code=link_code))
                else:
                    return redirect(url_for('worker.view_link', link_code=link_code))
            else:
                flash('사용자 정보를 찾을 수 없습니다.', 'error')
        else:
            flash('이름, 전화번호 또는 비밀번호가 일치하지 않습니다.', 'error')
            return render_template('auth/register_link.html', link=link)
    
    return render_template('auth/register_link.html', link=link) 
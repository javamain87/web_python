from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Link, UserType, AccessLog
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.index'))
        return redirect(url_for('auth.register_link'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('이름 또는 비밀번호가 올바르지 않습니다.', 'error')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        
        # 접속 로그 기록
        access_log = AccessLog(
            user_id=user.id,
            action='login',
            details=f'User logged in from {request.remote_addr}'
        )
        db.session.add(access_log)
        db.session.commit()
        
        if user.is_admin:
            return redirect(url_for('admin.index'))
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('auth.register_link')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='로그인', form=form)

@bp.route('/logout')
@login_required
def logout():
    # 로그아웃 전에 사용자 타입 저장
    is_admin = current_user.is_admin
    link_code = None
    
    # 신청자나 작업자인 경우 현재 보고 있던 링크 코드 저장
    if not is_admin:
        if current_user.user_type == 'applicant':
            link = Link.query.filter_by(applicant_id=current_user.id).first()
        else:  # worker
            link = Link.query.filter_by(worker_id=current_user.id).first()
        if link:
            link_code = link.link_code
    
    # 로그아웃 처리
    logout_user()
    
    # 관리자는 관리자 로그인 페이지로
    if is_admin:
        return redirect(url_for('auth.login'))
    
    # 신청자와 작업자는 링크 로그인 페이지로
    if link_code:
        return redirect(url_for('auth.register_link', link_code=link_code))
    else:
        # 링크를 찾을 수 없는 경우 기본 링크 로그인 페이지로
        return redirect(url_for('auth.register_link'))

@bp.route('/register_link', defaults={'link_code': None})
@bp.route('/register_link/<link_code>', methods=['GET', 'POST'])
def register_link(link_code):
    if link_code is None:
        return render_template('auth/register_link.html', link=None)
        
    link = Link.query.filter_by(link_code=link_code).first_or_404()
    
    if not link.is_active:
        flash('이 링크는 더 이상 사용할 수 없습니다.', 'error')
        return redirect(url_for('auth.register_link'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        if not name or not password or not phone:
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
                login_user(user)
                
                # 접속 로그 기록
                access_log = AccessLog(
                    user_id=user.id,
                    action='link_login',
                    details=f'User logged in via link from {request.remote_addr}'
                )
                db.session.add(access_log)
                db.session.commit()
                
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

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='회원가입', form=form) 
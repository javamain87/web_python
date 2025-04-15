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
    
    # 관리자용 공개 링크로 리다이렉트
    return redirect(url_for('admin.public_view_link', link_code=link_code)) 
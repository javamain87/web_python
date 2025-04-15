from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from app.models import User, Link, UserType
from app import db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return render_template('main/index.html') 
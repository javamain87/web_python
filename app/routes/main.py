from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User, Link, WorkLog, AccessLog
from app.forms import LinkForm
from datetime import datetime, timedelta
import secrets
import string
from sqlalchemy import func
from app.utils import admin_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.index'))
        else:
            return redirect(url_for('auth.register_link'))
    return redirect(url_for('auth.register_link'))

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.index'))
    elif current_user.user_type == 'worker':
        return redirect(url_for('worker.index'))
    elif current_user.user_type == 'applicant':
        return redirect(url_for('applicant.index'))
    return redirect(url_for('auth.register_link'))

@main.route('/create_link', methods=['GET', 'POST'])
@login_required
@admin_required
def create_link():
    form = LinkForm()
    if form.validate_on_submit():
        try:
            # Generate a unique link code
            while True:
                link_code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
                if not Link.query.filter_by(code=link_code).first():
                    break

            # Create new link
            link = Link(
                code=link_code,
                name=form.name.data,
                phone_number=form.phone_number.data,
                created_by=current_user.id,
                expires_at=datetime.utcnow() + timedelta(days=1)
            )
            db.session.add(link)
            db.session.commit()

            # Log the link creation
            access_log = AccessLog(
                user_id=current_user.id,
                action='create_link',
                details=f'Created link: {link_code}'
            )
            db.session.add(access_log)
            db.session.commit()

            flash('Link created successfully!', 'success')
            return redirect(url_for('admin.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating link: {str(e)}', 'danger')
            current_app.logger.error(f'Error creating link: {str(e)}')
    return render_template('main/create_link.html', form=form)

@main.route('/delete_link/<int:link_id>', methods=['POST'])
@login_required
@admin_required
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    try:
        # Log the link deletion
        access_log = AccessLog(
            user_id=current_user.id,
            action='delete_link',
            details=f'Deleted link: {link.code}'
        )
        db.session.add(access_log)
        
        db.session.delete(link)
        db.session.commit()
        flash('Link deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting link: {str(e)}', 'danger')
        current_app.logger.error(f'Error deleting link: {str(e)}')
    return redirect(url_for('admin.index')) 
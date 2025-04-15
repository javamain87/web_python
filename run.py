from app import create_app, db
from app.models import User, Link, WorkLog
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

app = create_app()

def init_db():
    with app.app_context():
        try:
            # Check if admin user already exists
            admin = User.query.filter_by(email='admin@example.com').first()
            if admin:
                print('Admin account already exists')
                return

            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                user_type='admin'
            )
            admin.is_admin = True
            admin.is_active = True
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Admin account created successfully')
            print('Username: admin')
            print('Password: admin123')
        except Exception as e:
            print(f'Error creating admin account: {e}')
            db.session.rollback()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Link': Link, 'WorkLog': WorkLog}

if __name__ == '__main__':
    with app.app_context():
        init_db()  # Initialize database and create admin account
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Check if admin user already exists
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print('Admin account already exists')
    else:
        # Create new admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('admin123')  # Set default password
        db.session.add(admin)
        db.session.commit()
        print('Admin account created successfully') 
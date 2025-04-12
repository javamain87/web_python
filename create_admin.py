from werkzeug.security import generate_password_hash
import psycopg2
from datetime import datetime

# 데이터베이스 연결 정보
db_params = {
    'host': 'dpg-cvt4v2h5pdvs739focv0-a.singapore-postgres.render.com',
    'database': 'web_app_db_fyrp',
    'user': 'web_app_db_fyrp_user',
    'password': 'tevnID7zCvPlwnbo0Xik5UXsYPRNacbG'
}

# 비밀번호 해시 생성
password = 'password'
password_hash = generate_password_hash(password, method='pbkdf2:sha256')

# SQL 쿼리
sql = """
INSERT INTO users (email, username, password_hash, is_admin, is_active, user_type, created_at, updated_at)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

# 데이터베이스 연결 및 쿼리 실행
try:
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    
    # 기존 admin 계정 삭제
    cur.execute("DELETE FROM users WHERE username = 'admin'")
    
    # 새 admin 계정 추가
    cur.execute(sql, (
        'admin@example.com',
        'admin',
        password_hash,
        True,
        True,
        'admin',
        datetime.utcnow(),
        datetime.utcnow()
    ))
    
    conn.commit()
    print("Admin account created successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    
finally:
    if cur:
        cur.close()
    if conn:
        conn.close() 
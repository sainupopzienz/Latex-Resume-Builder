import bcrypt
import secrets
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from database import get_db_cursor
from config import Config

def hash_password(password):
    salt = bcrypt.gensalt(rounds=Config.BCRYPT_LOG_ROUNDS)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def generate_session_token():
    return secrets.token_urlsafe(64)

def create_admin(email, password):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("SELECT id FROM admin_users WHERE email = %s", (email,))
        if cursor.fetchone():
            return None, "Admin with this email already exists"

        admin_id = str(uuid.uuid4())
        password_hash = hash_password(password)

        cursor.execute(
            "INSERT INTO admin_users (id, email, password_hash) VALUES (%s, %s, %s)",
            (admin_id, email, password_hash)
        )

        return admin_id, None

def login_admin(email, password):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("SELECT id, password_hash FROM admin_users WHERE email = %s", (email,))
        admin = cursor.fetchone()

        if not admin or not verify_password(password, admin['password_hash']):
            return None, "Invalid credentials"

        session_token = generate_session_token()
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=Config.SESSION_EXPIRY_HOURS)

        cursor.execute(
            "INSERT INTO admin_sessions (id, admin_id, session_token, expires_at) VALUES (%s, %s, %s, %s)",
            (session_id, admin['id'], session_token, expires_at)
        )

        cursor.execute(
            "UPDATE admin_users SET last_login = %s WHERE id = %s",
            (datetime.utcnow(), admin['id'])
        )

        return session_token, None

def verify_session(session_token):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            SELECT s.admin_id, s.expires_at, a.email
            FROM admin_sessions s
            JOIN admin_users a ON s.admin_id = a.id
            WHERE s.session_token = %s
            """,
            (session_token,)
        )
        session = cursor.fetchone()

        if not session:
            return None

        if datetime.fromisoformat(str(session['expires_at'])) < datetime.utcnow():
            cursor.execute("DELETE FROM admin_sessions WHERE session_token = %s", (session_token,))
            return None

        return session

def logout_admin(session_token):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM admin_sessions WHERE session_token = %s", (session_token,))

def clean_expired_sessions():
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM admin_sessions WHERE expires_at < %s", (datetime.utcnow(),))

def require_admin_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401

        session_token = auth_header.split(' ')[1]
        session = verify_session(session_token)

        if not session:
            return jsonify({'error': 'Invalid or expired session'}), 401

        request.admin_id = session['admin_id']
        request.admin_email = session['email']

        return f(*args, **kwargs)

    return decorated_function

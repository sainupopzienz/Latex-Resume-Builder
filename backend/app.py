from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import uuid
import json
from datetime import datetime
from config import Config
from database import get_db_cursor, init_db
from auth import login_admin, logout_admin, require_admin_auth, clean_expired_sessions
from validators import validate_resume_data, sanitize_resume_data
from pdf_generator import generate_resume_pdf

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={
    r"/api/*": {
        "origins": Config.ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.before_request
def before_request():
    if request.method == 'OPTIONS':
        return '', 204

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

## Admin creation must be performed via CLI script `create_admin.py` only.

@app.route('/api/admin/login', methods=['POST'])
def login_route():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    session_token, error = login_admin(data['email'], data['password'])

    if error:
        return jsonify({'error': error}), 401

    return jsonify({
        'message': 'Login successful',
        'session_token': session_token,
        'expires_in_hours': Config.SESSION_EXPIRY_HOURS
    }), 200

@app.route('/api/admin/logout', methods=['POST'])
@require_admin_auth
def logout_route():
    auth_header = request.headers.get('Authorization')
    session_token = auth_header.split(' ')[1]

    logout_admin(session_token)

    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/resumes', methods=['POST'])
def submit_resume():
    # Enforce max payload size to prevent abuse
    content_length = request.content_length or 0
    if content_length > Config.MAX_RESUME_SIZE:
        return jsonify({'error': 'Payload too large'}), 413

    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    errors = validate_resume_data(data)
    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400

    sanitized_data = sanitize_resume_data(data)

    resume_id = str(uuid.uuid4())

    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO resumes (
                    id, user_email, full_name, phone, social_links,
                    profile_summary, education, technical_skills,
                    work_experience, projects, languages, certifications
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    resume_id,
                    sanitized_data['user_email'],
                    sanitized_data['full_name'],
                    sanitized_data.get('phone'),
                    json.dumps(sanitized_data.get('social_links', {})),
                    sanitized_data.get('profile_summary'),
                    json.dumps(sanitized_data.get('education', [])),
                    json.dumps(sanitized_data.get('technical_skills', {})),
                    json.dumps(sanitized_data.get('work_experience', [])),
                    json.dumps(sanitized_data.get('projects', [])),
                    json.dumps(sanitized_data.get('languages', [])),
                    json.dumps(sanitized_data.get('certifications', []))
                )
            )

        return jsonify({
            'message': 'Resume submitted successfully',
            'resume_id': resume_id
        }), 201

    except Exception as e:
        app.logger.error(f"Error submitting resume: {str(e)}")
        return jsonify({'error': 'Failed to submit resume'}), 500

@app.route('/api/admin/resumes', methods=['GET'])
@require_admin_auth
def get_all_resumes():
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        offset = (page - 1) * per_page

        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT id, user_email, full_name, phone, created_at, updated_at
                FROM resumes
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                (per_page, offset)
            )
            resumes = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) as total FROM resumes")
            total = cursor.fetchone()['total']

        for resume in resumes:
            if resume.get('created_at'):
                resume['created_at'] = resume['created_at'].isoformat()
            if resume.get('updated_at'):
                resume['updated_at'] = resume['updated_at'].isoformat()

        return jsonify({
            'resumes': resumes,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }), 200

    except Exception as e:
        app.logger.error(f"Error fetching resumes: {str(e)}")
        return jsonify({'error': 'Failed to fetch resumes'}), 500

@app.route('/api/admin/resumes/<resume_id>', methods=['GET'])
@require_admin_auth
def get_resume_by_id(resume_id):
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT id, user_email, full_name, phone, social_links,
                       profile_summary, education, technical_skills,
                       work_experience, projects, languages, certifications,
                       created_at, updated_at
                FROM resumes
                WHERE id = %s
                """,
                (resume_id,)
            )
            resume = cursor.fetchone()

        if not resume:
            return jsonify({'error': 'Resume not found'}), 404

        for field in ['social_links', 'education', 'technical_skills', 'work_experience', 'projects', 'languages', 'certifications']:
            if resume.get(field):
                resume[field] = json.loads(resume[field])

        if resume.get('created_at'):
            resume['created_at'] = resume['created_at'].isoformat()
        if resume.get('updated_at'):
            resume['updated_at'] = resume['updated_at'].isoformat()

        return jsonify(resume), 200

    except Exception as e:
        app.logger.error(f"Error fetching resume: {str(e)}")
        return jsonify({'error': 'Failed to fetch resume'}), 500

@app.route('/api/admin/resumes/<resume_id>/pdf', methods=['GET'])
@require_admin_auth
def download_resume_pdf(resume_id):
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT user_email, full_name, phone, social_links,
                       profile_summary, education, technical_skills,
                       work_experience, projects, languages, certifications
                FROM resumes
                WHERE id = %s
                """,
                (resume_id,)
            )
            resume = cursor.fetchone()

        if not resume:
            return jsonify({'error': 'Resume not found'}), 404

        for field in ['social_links', 'education', 'technical_skills', 'work_experience', 'projects', 'languages', 'certifications']:
            if resume.get(field):
                resume[field] = json.loads(resume[field])

        pdf_buffer = generate_resume_pdf(resume)

        filename = f"{resume['full_name'].replace(' ', '_')}_resume.pdf"

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        app.logger.error(f"Error generating PDF: {str(e)}")
        return jsonify({'error': 'Failed to generate PDF'}), 500

@app.route('/api/admin/resumes/<resume_id>', methods=['DELETE'])
@require_admin_auth
def delete_resume(resume_id):
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM resumes WHERE id = %s", (resume_id,))

            if cursor.rowcount == 0:
                return jsonify({'error': 'Resume not found'}), 404

        return jsonify({'message': 'Resume deleted successfully'}), 200

    except Exception as e:
        app.logger.error(f"Error deleting resume: {str(e)}")
        return jsonify({'error': 'Failed to delete resume'}), 500

@app.route('/api/resumes/<resume_id>/pdf', methods=['GET'])
def public_download_pdf(resume_id):
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT user_email, full_name, phone, social_links,
                       profile_summary, education, technical_skills,
                       work_experience, projects, languages, certifications
                FROM resumes
                WHERE id = %s
                """,
                (resume_id,)
            )
            resume = cursor.fetchone()

        if not resume:
            return jsonify({'error': 'Resume not found'}), 404

        for field in ['social_links', 'education', 'technical_skills', 'work_experience', 'projects', 'languages', 'certifications']:
            if resume.get(field):
                resume[field] = json.loads(resume[field])

        pdf_buffer = generate_resume_pdf(resume)

        filename = f"{resume['full_name'].replace(' ', '_')}_resume.pdf"

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        app.logger.error(f"Error generating PDF: {str(e)}")
        return jsonify({'error': 'Failed to generate PDF'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    try:
        init_db()
        clean_expired_sessions()
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"Failed to start application: {str(e)}")

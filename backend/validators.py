import re
import bleach
from email_validator import validate_email, EmailNotValidError

def sanitize_text(text):
    if text is None:
        return None
    return bleach.clean(str(text), tags=[], strip=True)

def validate_email_format(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def validate_phone(phone):
    if not phone:
        return True
    phone_pattern = re.compile(r'^\+?[\d\s\-\(\)]{7,20}$')
    return bool(phone_pattern.match(phone))

def validate_url(url):
    if not url:
        return True
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(url_pattern.match(url))

def validate_resume_data(data):
    errors = []

    if not data.get('full_name'):
        errors.append('Full name is required')
    elif len(data['full_name']) > 255:
        errors.append('Full name is too long')

    if not data.get('user_email'):
        errors.append('Email is required')
    elif not validate_email_format(data['user_email']):
        errors.append('Invalid email format')

    if data.get('phone') and not validate_phone(data['phone']):
        errors.append('Invalid phone number format')

    social_links = data.get('social_links', {})
    if isinstance(social_links, dict):
        for key, url in social_links.items():
            if url and not validate_url(url):
                errors.append(f'Invalid URL for {key}')

    profile_summary = data.get('profile_summary', '')
    if profile_summary and len(profile_summary) > 5000:
        errors.append('Profile summary is too long (max 5000 characters)')

    return errors

def sanitize_resume_data(data):
    sanitized = {}

    sanitized['full_name'] = sanitize_text(data.get('full_name', ''))
    sanitized['user_email'] = sanitize_text(data.get('user_email', ''))
    sanitized['phone'] = sanitize_text(data.get('phone', ''))
    sanitized['profile_summary'] = sanitize_text(data.get('profile_summary', ''))

    social_links = data.get('social_links', {})
    if isinstance(social_links, dict):
        sanitized['social_links'] = {
            sanitize_text(k): sanitize_text(v)
            for k, v in social_links.items()
        }
    else:
        sanitized['social_links'] = {}

    for field in ['education', 'work_experience', 'projects', 'languages', 'certifications']:
        items = data.get(field, [])
        if isinstance(items, list):
            sanitized[field] = [
                {sanitize_text(k): sanitize_text(v) if isinstance(v, str) else v
                 for k, v in item.items()}
                if isinstance(item, dict) else sanitize_text(item)
                for item in items
            ]
        else:
            sanitized[field] = []

    technical_skills = data.get('technical_skills', {})
    if isinstance(technical_skills, dict):
        sanitized['technical_skills'] = {
            sanitize_text(k): [sanitize_text(skill) for skill in v]
            if isinstance(v, list) else sanitize_text(v)
            for k, v in technical_skills.items()
        }
    else:
        sanitized['technical_skills'] = {}

    return sanitized

# Resume Builder - Deployment Guide

## Overview

This is a full-stack resume builder application with a React frontend and Python Flask backend, using MySQL for data persistence. The application allows users to create professional resumes and provides an admin dashboard for managing submissions.

## Architecture

- **Frontend**: React + TypeScript + Vite + TailwindCSS
- **Backend**: Python Flask with security best practices
- **Database**: MySQL 8.0
- **Containerization**: Docker + Docker Compose

## Security Features

- Bcrypt password hashing with configurable salt rounds
- Session-based authentication with token expiration
- Input validation and sanitization (bleach library)
- SQL injection prevention via parameterized queries
- CORS configuration for allowed origins
- Environment variable configuration for secrets
- Non-root user in Docker container
- Health checks and proper error handling

## Prerequisites

- Docker and Docker Compose (recommended)
- OR Python 3.11+, Node.js 18+, and MySQL 8.0

## Quick Start with Docker

### 1. Clone and Configure

```bash
cd project
cp .env.example .env
```

Edit `.env` with your production values:
- Change `SECRET_KEY` to a strong random string
- Set secure database passwords
- Update `ALLOWED_ORIGINS` with your frontend URL

### 2. Build and Run

```bash
docker-compose up --build
```

This will:
- Start MySQL database
- Initialize database schema
- Start Flask backend on port 5000
- Backend available at http://localhost:5000

### 3. Create Admin Account

```bash
docker exec -it resume_builder_backend python create_admin.py admin@example.com SecurePassword123
```

### 4. Start Frontend (Development)

```bash
npm install
npm run dev
```

Frontend available at http://localhost:5173

## Manual Setup (Without Docker)

### Backend Setup

1. **Install MySQL** and create database:

```sql
CREATE DATABASE resume_builder;
CREATE USER 'resume_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON resume_builder.* TO 'resume_user'@'localhost';
FLUSH PRIVILEGES;
```

2. **Configure Backend**:

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your database credentials.

3. **Install Dependencies**:

```bash
pip install -r requirements.txt
```

4. **Initialize Database**:

```bash
python database.py
```

5. **Create Admin Account**:

```bash
python create_admin.py admin@example.com SecurePassword123
```

6. **Run Backend**:

```bash
python app.py
```

Or with Gunicorn (production):

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

### Frontend Setup

1. **Install Dependencies**:

```bash
npm install
```

2. **Configure Environment**:

```bash
cp .env.example .env
```

Edit `.env`:
```
VITE_API_URL=http://localhost:5000/api
```

3. **Run Development Server**:

```bash
npm run dev
```

4. **Build for Production**:

```bash
npm run build
```

## API Endpoints

### Public Endpoints

- `POST /api/resumes` - Submit a new resume
- `GET /api/resumes/:id/pdf` - Download resume PDF (public access)
- `GET /api/health` - Health check

### Admin Endpoints (Require Authentication)

- `POST /api/admin/login` - Admin login
- `POST /api/admin/logout` - Admin logout
- `GET /api/admin/resumes` - List all resumes (paginated)
- `GET /api/admin/resumes/:id` - Get resume details
- `GET /api/admin/resumes/:id/pdf` - Download resume PDF
- `DELETE /api/admin/resumes/:id` - Delete resume

### Admin Creation (CLI Only)

- `POST /api/admin/create` - Create admin account (use CLI script instead)

## API Usage Examples

### Submit Resume

```bash
curl -X POST http://localhost:5000/api/resumes \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "user_email": "john@example.com",
    "phone": "+1234567890",
    "profile_summary": "Experienced software engineer...",
    "education": [
      {
        "degree": "BS Computer Science",
        "institution": "University",
        "year": "2020",
        "gpa": "3.8"
      }
    ],
    "technical_skills": {
      "Languages": ["Python", "JavaScript", "TypeScript"]
    },
    "work_experience": [],
    "projects": [],
    "languages": [],
    "certifications": []
  }'
```

### Admin Login

```bash
curl -X POST http://localhost:5000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePassword123"
  }'
```

Response:
```json
{
  "message": "Login successful",
  "session_token": "token_here",
  "expires_in_hours": 24
}
```

### List Resumes (Admin)

```bash
curl -X GET http://localhost:5000/api/admin/resumes \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
```

## Database Schema

### Tables

1. **admin_users**
   - id (VARCHAR 36, PRIMARY KEY)
   - email (VARCHAR 255, UNIQUE)
   - password_hash (VARCHAR 255)
   - created_at (TIMESTAMP)
   - last_login (TIMESTAMP)

2. **resumes**
   - id (VARCHAR 36, PRIMARY KEY)
   - user_email (VARCHAR 255)
   - full_name (VARCHAR 255)
   - phone (VARCHAR 50)
   - social_links (JSON)
   - profile_summary (TEXT)
   - education (JSON)
   - technical_skills (JSON)
   - work_experience (JSON)
   - projects (JSON)
   - languages (JSON)
   - certifications (JSON)
   - created_at (TIMESTAMP)
   - updated_at (TIMESTAMP)

3. **admin_sessions**
   - id (VARCHAR 36, PRIMARY KEY)
   - admin_id (VARCHAR 36, FOREIGN KEY)
   - session_token (VARCHAR 255, UNIQUE)
   - expires_at (TIMESTAMP)
   - created_at (TIMESTAMP)

## Production Deployment

### Environment Variables (Required)

```bash
SECRET_KEY=<strong-random-key>
MYSQL_ROOT_PASSWORD=<secure-password>
MYSQL_PASSWORD=<secure-password>
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### Docker Production Build

```bash
docker-compose -f docker-compose.yml up -d
```

### Security Checklist

- [ ] Change all default passwords
- [ ] Set strong SECRET_KEY
- [ ] Configure ALLOWED_ORIGINS with actual domain
- [ ] Enable HTTPS/TLS for production
- [ ] Set up database backups
- [ ] Configure firewall rules
- [ ] Use secrets management (Docker secrets, Kubernetes secrets, etc.)
- [ ] Enable logging and monitoring
- [ ] Regular security updates

### Scaling Considerations

- Use a reverse proxy (Nginx/Traefik) for load balancing
- Increase Gunicorn workers based on CPU cores
- Set up database replication for high availability
- Use Redis for session storage in multi-instance deployments
- Implement rate limiting for API endpoints
- Use CDN for static frontend assets

## Monitoring & Maintenance

### Health Check

```bash
curl http://localhost:5000/api/health
```

### Clean Expired Sessions

Sessions are automatically cleaned on each admin login, but you can also run:

```python
from auth import clean_expired_sessions
clean_expired_sessions()
```

### Database Backup

```bash
docker exec resume_builder_mysql mysqldump -u root -p resume_builder > backup.sql
```

### View Logs

```bash
docker-compose logs -f backend
docker-compose logs -f mysql
```

## Troubleshooting

### Backend won't start

- Check MySQL is running: `docker-compose ps`
- Verify database credentials in `.env`
- Check logs: `docker-compose logs backend`

### Connection refused errors

- Ensure MySQL is healthy: `docker-compose ps`
- Wait for MySQL health check to pass (can take 30-60 seconds on first start)
- Verify network connectivity between containers

### Admin login fails

- Verify admin was created: Check admin_users table
- Ensure correct email/password
- Check session expiry settings

## Security Best Practices

1. **Never commit secrets** - Use `.env` files (gitignored)
2. **Use strong passwords** - Minimum 12 characters for production
3. **Regular updates** - Keep dependencies updated
4. **Input validation** - All user inputs are sanitized
5. **Parameterized queries** - SQL injection prevention
6. **HTTPS only** - Use TLS in production
7. **Rate limiting** - Implement on reverse proxy
8. **Audit logging** - Log all admin actions

## Support

For issues or questions, check:
- Application logs
- Docker container status
- Database connectivity
- Environment configuration

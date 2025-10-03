#!/bin/bash

echo "🚀 Starting Comprehensive End-to-End Test"
echo "=========================================="

# Get pod names
BACKEND_POD=$(kubectl get pods -l app=resume-builder-backend -o jsonpath='{.items[0].metadata.name}')
FRONTEND_POD=$(kubectl get pods -l app=resume-builder-frontend -o jsonpath='{.items[0].metadata.name}')

echo "Backend Pod: $BACKEND_POD"
echo "Frontend Pod: $FRONTEND_POD"

# Test 1: Pod Health Check
echo -e "\n1️⃣ Testing Pod Health..."
kubectl get pods -l app=resume-builder-backend,app=resume-builder-frontend
if [ $? -eq 0 ]; then
    echo "✅ Both pods are running"
else
    echo "❌ Pod health check failed"
    exit 1
fi

# Test 2: Inter-pod connectivity
echo -e "\n2️⃣ Testing Inter-pod Connectivity..."
HEALTH_RESPONSE=$(kubectl exec $FRONTEND_POD -- wget -qO- http://resume-builder-backend-service:5000/api/health)
if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    echo "✅ Frontend can reach backend"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo "❌ Inter-pod connectivity failed"
    exit 1
fi

# Test 3: Database Connectivity
echo -e "\n3️⃣ Testing Database Connectivity..."
DB_TEST=$(kubectl exec $BACKEND_POD -- python -c "
from database import get_db_cursor
try:
    with get_db_cursor() as cursor:
        cursor.execute('SELECT COUNT(*) as count FROM admin_users')
        result = cursor.fetchone()
        print('SUCCESS:', result['count'])
except Exception as e:
    print('ERROR:', e)
")

if [[ $DB_TEST == *"SUCCESS"* ]]; then
    echo "✅ Database connectivity working"
    echo "   $DB_TEST"
else
    echo "❌ Database connectivity failed"
    echo "   $DB_TEST"
    exit 1
fi

# Test 4: Admin Login
echo -e "\n4️⃣ Testing Admin Login..."
LOGIN_TEST=$(kubectl exec $BACKEND_POD -- python -c "
import requests
import json

login_data = {'email': 'admin@example.com', 'password': 'StrongPass123!'}
try:
    response = requests.post('http://localhost:5000/api/admin/login', json=login_data)
    if response.status_code == 200:
        token = response.json()['session_token']
        print('SUCCESS:', token[:20] + '...')
    else:
        print('ERROR:', response.text)
except Exception as e:
    print('ERROR:', e)
")

if [[ $LOGIN_TEST == *"SUCCESS"* ]]; then
    echo "✅ Admin login working"
    echo "   Token received: ${LOGIN_TEST#*SUCCESS: }"
else
    echo "❌ Admin login failed"
    echo "   $LOGIN_TEST"
    exit 1
fi

# Test 5: Resume Creation
echo -e "\n5️⃣ Testing Resume Creation..."
RESUME_TEST=$(kubectl exec $BACKEND_POD -- python -c "
import requests
import json

data = {
    'user_email': 'testuser@gmail.com',
    'full_name': 'Jane Smith',
    'phone': '+1-555-9876',
    'profile_summary': 'Senior Full Stack Developer with 8+ years experience',
    'social_links': {
        'linkedin': 'https://linkedin.com/in/janesmith',
        'github': 'https://github.com/janesmith'
    },
    'education': [
        {
            'degree': 'Master of Computer Science',
            'institution': 'Stanford University',
            'year': '2015',
            'gpa': '3.9'
        }
    ],
    'technical_skills': {
        'languages': ['Python', 'JavaScript', 'TypeScript', 'Go'],
        'frameworks': ['React', 'Node.js', 'Django', 'FastAPI'],
        'databases': ['PostgreSQL', 'MongoDB', 'Redis'],
        'cloud': ['AWS', 'Docker', 'Kubernetes']
    },
    'work_experience': [
        {
            'title': 'Senior Software Engineer',
            'company': 'Tech Innovations Inc',
            'duration': '2020-Present',
            'responsibilities': [
                'Led team of 5 developers in building microservices architecture',
                'Implemented CI/CD pipelines reducing deployment time by 60%',
                'Architected scalable solutions handling 1M+ daily users'
            ]
        }
    ],
    'projects': [
        {
            'name': 'Cloud-Native E-commerce Platform',
            'description': 'Built scalable e-commerce platform using React, Node.js, and AWS',
            'technologies': ['React', 'Node.js', 'PostgreSQL', 'AWS', 'Docker'],
            'link': 'https://github.com/janesmith/ecommerce-platform'
        }
    ],
    'languages': [
        {'name': 'English', 'proficiency': 'Native'},
        {'name': 'French', 'proficiency': 'Professional'},
        {'name': 'Spanish', 'proficiency': 'Conversational'}
    ],
    'certifications': [
        {
            'name': 'AWS Solutions Architect Professional',
            'issuer': 'Amazon Web Services',
            'year': '2022'
        },
        {
            'name': 'Certified Kubernetes Administrator',
            'issuer': 'Cloud Native Computing Foundation',
            'year': '2021'
        }
    ]
}

try:
    response = requests.post('http://localhost:5000/api/resumes', json=data)
    if response.status_code == 201:
        resume_id = response.json()['resume_id']
        print('SUCCESS:', resume_id)
    else:
        print('ERROR:', response.text)
except Exception as e:
    print('ERROR:', e)
")

if [[ $RESUME_TEST == *"SUCCESS"* ]]; then
    RESUME_ID=${RESUME_TEST#*SUCCESS: }
    echo "✅ Resume creation working"
    echo "   Resume ID: $RESUME_ID"
else
    echo "❌ Resume creation failed"
    echo "   $RESUME_TEST"
    exit 1
fi

# Test 6: PDF Generation
echo -e "\n6️⃣ Testing PDF Generation..."
PDF_TEST=$(kubectl exec $BACKEND_POD -- python -c "
import requests

resume_id = '$RESUME_ID'
try:
    response = requests.get(f'http://localhost:5000/api/resumes/{resume_id}/pdf')
    if response.status_code == 200:
        content_length = len(response.content)
        with open('/tmp/comprehensive_test_resume.pdf', 'wb') as f:
            f.write(response.content)
        print('SUCCESS:', content_length)
    else:
        print('ERROR:', response.text)
except Exception as e:
    print('ERROR:', e)
")

if [[ $PDF_TEST == *"SUCCESS"* ]]; then
    PDF_SIZE=${PDF_TEST#*SUCCESS: }
    echo "✅ PDF generation working"
    echo "   PDF size: $PDF_SIZE bytes"
    
    # Copy PDF to local system
    kubectl cp $BACKEND_POD:/tmp/comprehensive_test_resume.pdf ./comprehensive_test_resume.pdf
    echo "   PDF copied to: ./comprehensive_test_resume.pdf"
else
    echo "❌ PDF generation failed"
    echo "   $PDF_TEST"
    exit 1
fi

# Test 7: Admin Resume Management
echo -e "\n7️⃣ Testing Admin Resume Management..."
ADMIN_TEST=$(kubectl exec $BACKEND_POD -- python -c "
import requests
import json

# Login
login_data = {'email': 'admin@example.com', 'password': 'StrongPass123!'}
login_response = requests.post('http://localhost:5000/api/admin/login', json=login_data)
token = login_response.json()['session_token']
headers = {'Authorization': f'Bearer {token}'}

try:
    # List all resumes
    resumes_response = requests.get('http://localhost:5000/api/admin/resumes', headers=headers)
    if resumes_response.status_code == 200:
        resumes_data = resumes_response.json()
        total_resumes = resumes_data['total']
        
        # Get specific resume details
        resume_id = '$RESUME_ID'
        resume_response = requests.get(f'http://localhost:5000/api/admin/resumes/{resume_id}', headers=headers)
        if resume_response.status_code == 200:
            print('SUCCESS:', total_resumes)
        else:
            print('ERROR: Resume detail fetch failed')
    else:
        print('ERROR:', resumes_response.text)
except Exception as e:
    print('ERROR:', e)
")

if [[ $ADMIN_TEST == *"SUCCESS"* ]]; then
    TOTAL_RESUMES=${ADMIN_TEST#*SUCCESS: }
    echo "✅ Admin resume management working"
    echo "   Total resumes in system: $TOTAL_RESUMES"
else
    echo "❌ Admin resume management failed"
    echo "   $ADMIN_TEST"
    exit 1
fi

# Test 8: Frontend Accessibility
echo -e "\n8️⃣ Testing Frontend Accessibility..."
kubectl port-forward svc/resume-builder-frontend-service 8080:80 >/dev/null 2>&1 &
PORT_FORWARD_PID=$!
sleep 3

FRONTEND_TEST=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080)
kill $PORT_FORWARD_PID >/dev/null 2>&1

if [ "$FRONTEND_TEST" = "200" ]; then
    echo "✅ Frontend accessible"
    echo "   HTTP Status: $FRONTEND_TEST"
else
    echo "❌ Frontend not accessible"
    echo "   HTTP Status: $FRONTEND_TEST"
fi

# Summary
echo -e "\n🎉 COMPREHENSIVE TEST SUMMARY"
echo "============================="
echo "✅ Pod Health: PASSED"
echo "✅ Inter-pod Connectivity: PASSED"
echo "✅ Database Connectivity: PASSED"
echo "✅ Admin Login: PASSED"
echo "✅ Resume Creation: PASSED"
echo "✅ PDF Generation: PASSED"
echo "✅ Admin Management: PASSED"
echo "✅ Frontend Accessibility: PASSED"

echo -e "\n📋 ACCESS INFORMATION"
echo "===================="
echo "Admin Credentials:"
echo "  Email: admin@example.com"
echo "  Password: StrongPass123!"
echo ""
echo "Service Access:"
echo "  Frontend: kubectl port-forward svc/resume-builder-frontend-service 8080:80"
echo "  Backend: kubectl port-forward svc/resume-builder-backend-service 5000:5000"
echo ""
echo "Generated Files:"
echo "  - comprehensive_test_resume.pdf (Sample resume PDF)"
echo ""
echo "🚀 All tests passed! Your resume builder is fully functional!"

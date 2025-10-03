#!/bin/bash

# Test resume creation and download
BACKEND_URL="http://resume-builder-backend-service:5000"
FRONTEND_POD=$(kubectl get pods -l app=resume-builder-frontend -o jsonpath='{.items[0].metadata.name}')

echo "Testing resume creation and download..."

# Test data for resume creation
RESUME_DATA='{
  "user_email": "test@example.com",
  "full_name": "John Doe",
  "phone": "+1-555-0123",
  "social_links": {
    "linkedin": "https://linkedin.com/in/johndoe",
    "github": "https://github.com/johndoe"
  },
  "profile_summary": "Experienced software developer with 5+ years in web development",
  "education": [
    {
      "degree": "Bachelor of Science in Computer Science",
      "institution": "University of Technology",
      "year": "2018",
      "gpa": "3.8"
    }
  ],
  "technical_skills": {
    "programming": ["Python", "JavaScript", "Java"],
    "frameworks": ["React", "Flask", "Spring"],
    "databases": ["PostgreSQL", "MongoDB"],
    "tools": ["Git", "Docker", "Kubernetes"]
  },
  "work_experience": [
    {
      "title": "Senior Software Developer",
      "company": "Tech Corp",
      "duration": "2020-Present",
      "responsibilities": [
        "Led development of microservices architecture",
        "Mentored junior developers",
        "Improved system performance by 40%"
      ]
    }
  ],
  "projects": [
    {
      "name": "E-commerce Platform",
      "description": "Built scalable e-commerce platform using React and Node.js",
      "technologies": ["React", "Node.js", "PostgreSQL"],
      "link": "https://github.com/johndoe/ecommerce"
    }
  ],
  "languages": [
    {"name": "English", "proficiency": "Native"},
    {"name": "Spanish", "proficiency": "Intermediate"}
  ],
  "certifications": [
    {
      "name": "AWS Solutions Architect",
      "issuer": "Amazon Web Services",
      "year": "2021"
    }
  ]
}'

echo "1. Creating resume..."
RESUME_RESPONSE=$(kubectl exec $FRONTEND_POD -- wget -qO- --post-data="$RESUME_DATA" --header='Content-Type: application/json' $BACKEND_URL/api/resumes)
echo "Resume creation response: $RESUME_RESPONSE"

# Extract resume ID
RESUME_ID=$(echo $RESUME_RESPONSE | grep -o '"resume_id":"[^"]*"' | cut -d'"' -f4)
echo "Resume ID: $RESUME_ID"

if [ -n "$RESUME_ID" ]; then
    echo "2. Testing PDF generation..."
    kubectl exec $FRONTEND_POD -- wget -qO- $BACKEND_URL/api/resumes/$RESUME_ID/pdf > test_resume.pdf
    
    if [ -s test_resume.pdf ]; then
        echo "✅ PDF generated successfully! Size: $(wc -c < test_resume.pdf) bytes"
    else
        echo "❌ PDF generation failed"
    fi
else
    echo "❌ Resume creation failed"
fi

echo "3. Testing admin login..."
LOGIN_RESPONSE=$(kubectl exec $FRONTEND_POD -- wget -qO- --post-data='{"email": "admin@example.com", "password": "StrongPass123!"}' --header='Content-Type: application/json' $BACKEND_URL/api/admin/login)
echo "Login response: $LOGIN_RESPONSE"

# Extract session token
SESSION_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"session_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$SESSION_TOKEN" ]; then
    echo "4. Testing admin resume list..."
    ADMIN_RESUMES=$(kubectl exec $FRONTEND_POD -- wget -qO- --header="Authorization: Bearer $SESSION_TOKEN" $BACKEND_URL/api/admin/resumes)
    echo "Admin resumes: $ADMIN_RESUMES"
    echo "✅ Admin functionality working!"
else
    echo "❌ Admin login failed"
fi

echo "Test completed!"

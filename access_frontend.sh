#!/bin/bash

echo "🌐 Starting Frontend Access"
echo "=========================="

echo "Setting up port forwarding to access the frontend..."
echo "Frontend will be available at: http://localhost:8080"
echo ""
echo "Admin Login Credentials:"
echo "  Email: admin@example.com"
echo "  Password: StrongPass123!"
echo ""
echo "Press Ctrl+C to stop the port forwarding"
echo ""

kubectl port-forward svc/resume-builder-frontend-service 8080:80

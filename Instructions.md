#Latex_Resume_Builder
docker compose ps


#below is the command to create the first admin user

#use service name
docker compose exec backend python create_admin.py admin@example.com 'StrongPass123!'

or

#use container name
docker exec -it resume_builder_backend python create_admin.py admin@example.com 'StrongPass123!'


#output is below:
Admin created successfully!
Admin ID: f6d197f2-702d-4148-8d72-78c103df50e0
Email: admin@example.com


#Isssue fixed (env was not updated correct it need to set on build time default was localhost:5000/api for frontend VITE_API_URL)
docker build -f frontend.Dockerfile --build-arg VITE_API_URL=http://alb-new-1295629679.us-east-1.elb.amazonaws.com/api -t sainupopzienz/resume-ui:v7 .


#loadbalancer level change

The ALB routing is now working correctly. The 405 error is fixed. The issue was exactly what I identified:

Problem: ALB listener rule was configured with path pattern /api instead of /api/*
Solution: You changed it to /api/* in the console, which now correctly routes all API requests.

Now you need to update your frontend to use the ALB URL instead of the direct NodePort. Update your frontend environment variable:


#curl test API working

I will run the following shell command: 
curl -X POST http://alb-new-1295629679.us-east-1.elb.amazonaws.com/api/resumes \
  -H "Content-Type: application/json" \
  -d '{"personalInfo":{"fullName":"John Doe","email":"john.doe@example.com","phone":"123-456-7890","location":"New York"},"sections":[]}' \
  -v
  
  > Perfect! Updated successfully:

## Changes Applied:
✅ Frontend v7: Now calls http://alb-new-1295629679.us-east-1.elb.amazonaws.com/api
✅ Backend CORS: Allows http://alb-new-1295629679.us-east-1.elb.amazonaws.com
✅ Deployed: Both services updated and running



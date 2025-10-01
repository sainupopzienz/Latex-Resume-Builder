

# run app on anywhere
docker compose build
docker compose up -d
docker compose logs -f

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
Admin ID: cb1fe31b-bc27-4221-9960-065cf4cf27e3
Email: admin@example.com



# 

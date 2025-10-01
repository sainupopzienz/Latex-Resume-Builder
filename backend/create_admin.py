import sys
from auth import create_admin

def main():
    if len(sys.argv) != 3:
        print("Usage: python create_admin.py <email> <password>")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    if len(password) < 8:
        print("Error: Password must be at least 8 characters long")
        sys.exit(1)

    admin_id, error = create_admin(email, password)

    if error:
        print(f"Error: {error}")
        sys.exit(1)

    print(f"Admin created successfully!")
    print(f"Admin ID: {admin_id}")
    print(f"Email: {email}")

if __name__ == '__main__':
    main()

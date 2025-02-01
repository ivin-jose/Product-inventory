
from main import app, db, AuthUser
import uuid
from werkzeug.security import generate_password_hash

''' admin added '''

# Create a sample admin user
# admin_user = AuthUser(
#     id=str(uuid.uuid4()),
#     username="admin",
#     email="admin@mail.com",
#     password=generate_password_hash("123456")  # Encrypt password
# )

# with app.app_context():
#     # Check if the admin user already exists
#     existing_user = AuthUser.query.filter_by(email="admin@mail.com").first()
#     if not existing_user:
#         db.session.add(admin_user)
#         db.session.commit()
#         print("✅ Admin user added successfully!")
#     else:
#         print("⚠️ Admin user already exists.")



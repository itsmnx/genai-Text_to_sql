# create_user.py
from auth.auth import auth_manager

result = auth_manager.register_user('tanmay', 'tanmay12345', 'tanmay@gmail.com')
print(f"Result: {result}")
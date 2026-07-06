import os
# pyrefly: ignore [missing-import]
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

# pyrefly: ignore [missing-import]
from django.contrib.auth.models import User

# Fetch credentials from env, otherwise fall back to default
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@library.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser '{username}'...")
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created successfully.")
else:
    print(f"Superuser '{username}' already exists.")

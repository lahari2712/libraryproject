import os
import django  # pyrefly: ignore [missing-import]

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryproject.settings')
django.setup()

from django.contrib.auth.models import User  # pyrefly: ignore [missing-import]

username = "admin"
email = "admin@gmail.com"
password = "admin123"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
    )
    print("Superuser created.")
else:
    print("Superuser already exists.")
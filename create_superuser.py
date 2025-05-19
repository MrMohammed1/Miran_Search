import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "miran_search.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
if not User.objects.filter(username="testuser").exists():
    User.objects.create_superuser("testuser", "admin@example.com", "testpass")
    
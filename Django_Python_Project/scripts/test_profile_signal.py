import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','Django_Python_Project.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.models import Profile

User = get_user_model()

try:
    u = User.objects.create_user(username='testuser_tmp3', email='tmpemail+test3@example.com', password='Testpass123!')
    print('User created', u.pk, u.email)
    p = Profile.objects.get(user=u)
    print('Profile created with email:', p.email)
finally:
    try:
        p.delete()
    except Exception:
        pass
    try:
        u.delete()
    except Exception:
        pass
    print('Cleanup done')

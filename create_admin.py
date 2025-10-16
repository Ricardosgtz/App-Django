import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MyDjangoProjectServer.settings")
django.setup()

from django.contrib.auth.models import User

username = "ricrado_admin"
email = "ricardosantosgutierrez9@gmail.com"
password = "admin123"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("✅ Usuario administrador creado correctamente.")
else:
    print("⚠️ El usuario administrador ya existe.")

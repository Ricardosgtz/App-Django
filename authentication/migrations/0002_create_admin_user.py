from django.db import migrations

def create_admin_user(apps, schema_editor):
    from django.contrib.auth.models import User
    username = "admin"
    email = "admin@gmail.com"
    password = "admin123"

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print("✅ Superusuario creado correctamente desde migración.")
    else:
        print("⚠️ El superusuario ya existía.")


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),  # Ajusta si tu primera migración tiene otro nombre
    ]

    operations = [
        migrations.RunPython(create_admin_user),
    ]

from django.db import models

# Create your models here.
class Client(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, db_column='nombre')
    lastname = models.CharField(max_length=45, db_column='apellido')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10, db_column='telefono')
    image = models.CharField(max_length=255, null=True, blank=False, db_column='imagen')
    password = models.CharField(max_length=60)
    created_at = models.DateTimeField(db_column='fecha_creacion', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='fecha_actualizacion', auto_now=True)


    class Meta:
        db_table = 'clientes'

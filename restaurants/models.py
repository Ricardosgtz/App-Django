from django.db import models

class Restaurant(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, db_column='nombre', null=True, blank=True)
    address = models.CharField(max_length=255, db_column='direccion', null=True, blank=True)
    email = models.EmailField(max_length=45, db_column='email', null=True, blank=True)
    phone = models.CharField(max_length=10, db_column='telefono', null=True, blank=True)
    opening_time = models.TimeField(db_column='horario_apertura', null=True, blank=True)
    closing_time = models.TimeField(db_column='horario_cierre', null=True, blank=True)
    logo = models.CharField(max_length=255, db_column='logo', null=True, blank=True)
    status = models.BooleanField(db_column='estatus', null=True, blank=True)
    account_number = models.CharField(
        max_length=20,
        db_column='numero_cuenta',
        null=True,
        blank=True,
        help_text="Número de cuenta bancaria"
    )
    clabe = models.CharField(
        max_length=20,
        db_column='clabe',
        null=True,
        blank=True,
        help_text="CLABE interbancaria"
    )

    class Meta:
        db_table = 'restaurantes'

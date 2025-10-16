from django.db import models

class OrderStatus(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, db_column='nombre', null=True, blank=True)
    description = models.CharField(max_length=255, db_column='descripcion', null=True, blank=True)
    created_at = models.DateTimeField(db_column='fecha_creacion', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='fecha_actualizacion', auto_now=True)

    class Meta:
        db_table = 'estatus_ordenes'

    def __str__(self):
        return self.name or 'Estatus sin nombre'

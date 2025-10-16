from django.db import models

class Address(models.Model):
    id = models.AutoField(primary_key=True)
    alias = models.CharField(max_length=100, null=True, blank=True, db_column='alias')
    address = models.CharField(max_length=255, null=True, blank=True, db_column='direccion')
    reference = models.CharField(max_length=255, null=True, blank=True, db_column='referencia')
    created_at = models.DateTimeField(auto_now_add=True, db_column='fecha_creacion')
    updated_at = models.DateTimeField(auto_now=True, db_column='fecha_actualizacion')
    id_client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        db_column='clienteId',
        related_name='addresses'
    )

    class Meta:
        db_table = 'direcciones'
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'{self.alias or "No alias"} - {self.address}'

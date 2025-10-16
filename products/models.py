from django.db import models

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, db_column='nombre', null=True, blank=True)
    description = models.CharField(max_length=255, db_column='descripcion', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, db_column='precio', null=True, blank=True)
    image1 = models.CharField(max_length=255, db_column='imagen1', null=True, blank=True)
    image2 = models.CharField(max_length=255, db_column='imagen2', null=True, blank=True)
    available = models.BooleanField(db_column='disponible', null=True, blank=True)
    created_at = models.DateTimeField(db_column='fecha_creacion', null=True, blank=True)
    updated_at = models.DateTimeField(db_column='fecha_actualizacion', null=True, blank=True)

    id_category = models.ForeignKey(
        'categories.Category',
        on_delete=models.CASCADE,
        db_column='categoriaId',
        related_name='products',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'productos'


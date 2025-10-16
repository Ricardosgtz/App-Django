from django.db import models

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, db_column='nombre', null=True, blank=True)
    description = models.TextField(db_column='descripcion', null=True, blank=True)
    image = models.CharField(max_length=255, db_column='imagen', null=True, blank=True)
    created_at = models.DateTimeField(db_column='fecha_creacion', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='fecha_actualizacion', auto_now=True)

    id_restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.CASCADE,
        db_column='restauranteId',
        related_name='categories',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'categorias'

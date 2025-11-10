# orders/models.py
from django.db import models


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(db_column='fecha_creacion', auto_now_add=True)
    order_type = models.CharField(
        max_length=20,
        db_column='tipo_pedido',
        choices=[
            ('sitio', 'Sitio'),
            ('domicilio', 'Domicilio'),
            ('anticipado', 'Anticipado'),
        ],
        null=True,
        blank=True
    )
    note = models.TextField(db_column='nota', null=True, blank=True)

    arrival_time = models.TimeField(
        db_column='hora_llegada',
        null=True,
        blank=True,
        help_text="Hora de llegada para órdenes anticipadas (15:00–23:00)"
    )

    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.SET_NULL,
        db_column='clienteId',
        related_name='orders',
        null=True,
        blank=True
    )
    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.SET_NULL,
        db_column='restauranteId',
        related_name='orders',
        null=True,
        blank=True
    )
    status = models.ForeignKey(
        'orderstatus.OrderStatus',
        on_delete=models.SET_NULL,
        db_column='estatusId',
        related_name='orders',
        null=True,
        blank=True
    )
    address = models.ForeignKey(
        'address.Address',
        on_delete=models.SET_NULL,
        db_column='direccionId',
        related_name='orders',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'ordenes'
        ordering = ['-created_at']

    def __str__(self):
        return f'Orden #{self.id}'

    def get_total(self):
        """Calcula el total de la orden sumando todos los detalles"""
        return sum(
            detail.unit_price * detail.quantity 
            for detail in self.orderdetails.all()
        )


class OrderDetail(models.Model):
    id = models.AutoField(primary_key=True)

    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        db_column='ordenId',
        related_name='orderdetails'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        db_column='productoId',
        related_name='order_details'
    )
    quantity = models.IntegerField(db_column='cantidad')
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column='precio_unitario'
    )
    created_at = models.DateTimeField(db_column='fecha_creacion', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='fecha_actualizacion', auto_now=True)

    class Meta:
        db_table = 'detalles_ordenes'
        managed = True  # Si alguna vez se vuelve False, Django no tocará la tabla
        ordering = ['id']

    def __str__(self):
        return f'Detalle Orden #{self.order.id} - Producto #{self.product.id}'

    def get_subtotal(self):
        """Calcula el subtotal del detalle"""
        return self.unit_price * self.quantity

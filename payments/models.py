from django.db import models


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
    ]

    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('rechazado', 'Rechazado'),
        ('reembolsado', 'Reembolsado'),
    ]

    id = models.AutoField(primary_key=True)

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        null=True,
        blank=True,
        db_column='metodo_pago',
        help_text='Método de pago (efectivo o transferencia)',
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendiente',
        null=True,
        blank=True,
        db_column='estatus',
        help_text='Estado del pago (pendiente, confirmado, rechazado o reembolsado)',
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='monto',
        help_text='Monto total del pago',
    )

    receipt = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column='comprobante',
        help_text='Comprobante del pago (URL o texto)',
    )

    payment_date = models.DateTimeField(
        auto_now_add=True,
        db_column='fecha_pago',
        help_text='Fecha y hora del pago',
    )

    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.DO_NOTHING,  # 👈 Coincide con ON DELETE NO ACTION
        db_column='ordenId',
        related_name='payments',
        null=True,
        blank=True,
        help_text='Orden asociada al pago',
    )

    class Meta:
        db_table = 'pagos'
        managed = False  # 👈 No se recreará ni modificará en migraciones
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-payment_date']

    def __str__(self):
        return f'Pago #{self.id} - {self.payment_method or "N/A"} - {self.status or "N/A"}'

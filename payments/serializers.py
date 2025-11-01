from rest_framework import serializers
from payments.models import Payment
from orders.models import Order
from django.utils import timezone  # 👈 importante

class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        source='order',
        write_only=True
    )
    order = serializers.SerializerMethodField()
    payment_date = serializers.SerializerMethodField()  # 👈 usamos método personalizado

    class Meta:
        model = Payment
        fields = [
            'id',
            'payment_method',
            'status',
            'amount',
            'receipt',
            'payment_date',
            'order_id',
            'order'
        ]
        read_only_fields = ['status', 'amount', 'payment_date']

    def get_payment_date(self, obj):
        """Convierte la hora UTC a la hora local configurada (México)."""
        if obj.payment_date:
            local_time = timezone.localtime(obj.payment_date)
            return local_time.strftime("%Y-%m-%d %H:%M:%S")  # 👈 hora local visible
        return None

    def get_order(self, obj):
        if obj.order:
            return {
                'id': obj.order.id,
                'type': obj.order.order_type,
                'status': obj.order.status.name if obj.order.status else None,
                'total': obj.order.get_total()
            }
        return None

from rest_framework import serializers
from payments.models import Payment
from orders.models import Order

class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        source='order',
        write_only=True
    )
    order = serializers.SerializerMethodField()

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

    def get_order(self, obj):
        if obj.order:
            return {
                'id': obj.order.id,
                'type': obj.order.order_type,
                'status': obj.order.status.name if obj.order.status else None,
                'total': obj.order.get_total()
            }
        return None

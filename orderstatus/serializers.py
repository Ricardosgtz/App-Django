from rest_framework import serializers
from orderstatus.models import OrderStatus


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ['id', 'name', 'description']

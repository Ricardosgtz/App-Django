# orders/serializers.py
from datetime import time
from rest_framework import serializers
from orders.models import Order, OrderDetail
from products.serializers import ProductSerializer
from django.db import transaction
from orderstatus.models import OrderStatus


class OrderDetailSerializer(serializers.ModelSerializer):
    """Serializer para los detalles de una orden (productos)"""
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderDetail
        fields = ['product_id', 'product', 'quantity', 'unit_price', 'subtotal']

    def get_subtotal(self, obj):
        return obj.get_subtotal()


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer para listar órdenes del cliente"""
    client = serializers.SerializerMethodField()
    restaurant = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    order_details_count = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'client', 'restaurant', 'order', 'address',
            'status', 'total', 'order_details_count', 'created_at'
        ]

    def get_client(self, obj):
        return {
            'id': obj.client.id,
            'name': obj.client.name
        }

    def get_restaurant(self, obj):
        return {
            'id': obj.restaurant.id,
            'name': obj.restaurant.name
        }

    def get_order(self, obj):
        return {
            'type': obj.order_type,
            'note': obj.note
        }

    def get_address(self, obj):
        if obj.address:
            return {
                'alias': obj.address.alias,
                'address': obj.address.address
            }
        return None

    def get_status(self, obj):
        if obj.status:
            return {
                'id': obj.status.id,
                'name': obj.status.name,
                'description': obj.status.description
            }
        return None

    def get_order_details_count(self, obj):
        return obj.orderdetails.count()

    def get_total(self, obj):
        return obj.get_total()


class OrderRetrieveSerializer(serializers.ModelSerializer):
    """Serializer para ver el detalle completo de una orden"""
    client = serializers.SerializerMethodField()
    restaurant = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()
    orderdetails = OrderDetailSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    arrival_time = serializers.TimeField(read_only=True) 


    class Meta:
        model = Order
        fields = [
            'id', 'client', 'restaurant', 'address',
            'order', 'status', 'orderdetails', 'total', 'arrival_time', 'created_at'
        ]

    def get_client(self, obj):
        return {
            'id': obj.client.id,
            'name': obj.client.name,
            'lastname': obj.client.lastname,
            'email': obj.client.email,
            'phone': obj.client.phone
        }

    def get_restaurant(self, obj):
        return {
            'id': obj.restaurant.id,
            'name': obj.restaurant.name
        }

    def get_address(self, obj):
        if obj.address:
            return {
                'id': obj.address.id,
                'alias': obj.address.alias,
                'address': obj.address.address,
                'reference': obj.address.reference
            }
        return None

    def get_status(self, obj):
        if obj.status:
            return {
                'id': obj.status.id,
                'name': obj.status.name,
                'description': obj.status.description
            }
        return None

    def get_order(self, obj):
        return {
            'type': obj.order_type,
            'note': obj.note
        }

    def get_total(self, obj):
        return obj.get_total()


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear una orden con sus productos"""
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True
    )
    arrival_time = serializers.TimeField(required=False, allow_null=True)

    class Meta:
        model = Order
        fields = [
            'client', 'restaurant', 'address',
            'order_type', 'note', 'items', 'status', 'arrival_time'
        ]

    def validate(self, data):
        order_type = data.get('order_type')
        address = data.get('address')
        client = data.get('client')
        arrival_time = data.get('arrival_time')
        request = self.context.get('request')

        # 🔒 Validar cliente autenticado
        if request and request.user.is_authenticated:
            if client.id != request.user.id:
                raise serializers.ValidationError({'client': 'Solo puedes crear órdenes para ti mismo'})

        # 📍 Validar dirección según tipo de pedido
        if order_type == 'domicilio' and not address:
            raise serializers.ValidationError({'address': 'La dirección es requerida para pedidos a domicilio'})
        if order_type in ['sitio', 'anticipado']:
            data['address'] = None

        # 🕒 Validar horario de llegada para órdenes anticipadas
        if order_type == 'anticipado':
            if not arrival_time:
                raise serializers.ValidationError({
                    'arrival_time': 'Debes seleccionar una hora de llegada para órdenes anticipadas.'
                })

            start_time = time(15, 0)
            end_time = time(23, 0)

            if not (start_time <= arrival_time <= end_time):
                raise serializers.ValidationError({
                    'arrival_time': 'La hora de llegada debe estar entre las 15:00 y las 23:00.'
                })

        # 🚫 Si el pedido NO es anticipado, limpiar arrival_time
        if order_type != 'anticipado':
            data['arrival_time'] = None

        return data

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("La orden debe contener al menos un producto")

        for item in value:
            if 'product_id' not in item or 'quantity' not in item or 'unit_price' not in item:
                raise serializers.ValidationError("Cada producto debe tener product_id, quantity y unit_price")
            if item['quantity'] < 1:
                raise serializers.ValidationError("La cantidad debe ser mayor a 0")
            if float(item['unit_price']) < 0:
                raise serializers.ValidationError("El precio no puede ser negativo")
        return value

    @transaction.atomic
    def create(self, validated_data):
        """Crea la orden y sus detalles en una transacción"""
        items = validated_data.pop('items', [])

        # ✅ Asignar estado pendiente si no se envía
        if not validated_data.get('status'):
            validated_data['status'] = OrderStatus.objects.filter(id=1).first()

        # 🧾 Crear la orden
        order = Order.objects.create(**validated_data)

        # 🛒 Crear cada producto de la orden
        details = [
            OrderDetail(
                order=order,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item['unit_price']
            )
            for item in items
        ]
        OrderDetail.objects.bulk_create(details)  # ✅ inserta todos de golpe (más rápido y confiable)

        return order
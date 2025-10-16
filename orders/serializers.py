# orders/serializers.py
from rest_framework import serializers
from orders.models import Order, OrderDetail
from products.serializers import ProductSerializer


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

    class Meta:
        model = Order
        fields = [
            'id', 'client', 'restaurant', 'address',
            'order', 'status', 'orderdetails', 'total', 'created_at'
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
    """Serializer para crear una orden"""
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True
    )

    class Meta:
        model = Order
        fields = ['client', 'restaurant', 'address', 'order_type', 'note', 'items', 'status']

    def validate(self, data):
        """Valida que la dirección sea requerida solo para pedidos a domicilio"""
        order_type = data.get('order_type')
        address = data.get('address')
        client = data.get('client')
        
        # Validar que el cliente sea el usuario autenticado
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # request.user es un objeto Client, acceder directamente a su id
            if client.id != request.user.id:
                raise serializers.ValidationError({
                    'client': 'Solo puedes crear órdenes para ti mismo'
                })

        # Si es domicilio, la dirección es obligatoria
        if order_type == 'domicilio' and not address:
            raise serializers.ValidationError({
                'address': 'La dirección es requerida para pedidos a domicilio'
            })

        # Si es sitio o anticipado, la dirección no se debe enviar (o será None)
        if order_type in ['sitio', 'anticipado']:
            data['address'] = None

        return data

    def validate_items(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError("La orden debe contener al menos un producto")
        
        for item in value:
            if 'product_id' not in item or 'quantity' not in item or 'unit_price' not in item:
                raise serializers.ValidationError(
                    "Cada item debe tener: product_id, quantity, unit_price"
                )
            if item['quantity'] < 1:
                raise serializers.ValidationError("La cantidad debe ser mayor a 0")
            if item['unit_price'] < 0:
                raise serializers.ValidationError("El precio no puede ser negativo")
        
        return value

    def create(self, validated_data):
        from orderstatus.models import OrderStatus
        
        items = validated_data.pop('items')
        
        # Si no proporcionan status, asignar "Pendiente" (id=1)
        if not validated_data.get('status'):
            try:
                pending_status = OrderStatus.objects.get(id=1)
                validated_data['status'] = pending_status
            except OrderStatus.DoesNotExist:
                pass
        
        order = Order.objects.create(**validated_data)

        for item in items:
            OrderDetail.objects.create(
                order=order,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item['unit_price']
            )

        return order
from rest_framework import serializers

from address.models import Address
from clients.models import Client

class AddressSerializer(serializers.ModelSerializer):
    alias = serializers.CharField(
        required=True, 
        allow_blank=False,
        error_messages={'blank': 'El alias no puede estar vacia'}
    )
    address = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={'blank': 'La direccion no puede estar vacia'}
    )
    reference = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={'blank': 'La refencia no puede estar vacia'}
    )
    class Meta:
        model = Address
        fields = ['id', 'id_client', 'alias', 'address', 'reference', 'created_at', 'updated_at']
        read_only_fields = ['id_client']
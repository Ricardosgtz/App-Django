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
    id_client = serializers.PrimaryKeyRelatedField(
        queryset = Client.objects.all(),
        error_messages = {'does_not_exist': 'El Cliente no existe'}
    )
    class Meta:
        model = Address
        fields = ['id', 'id_client', 'alias', 'address', 'reference', 'created_at', 'updated_at']
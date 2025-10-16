from rest_framework import serializers
from .models import Client
import bcrypt

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'lastname', 'email', 'phone', 'image', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        raw_password = validated_data.pop('password')
        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())
        validated_data['password'] = hashed_password.decode('utf-8')
        client = Client.objects.create(**validated_data)
        return client


from rest_framework import serializers
from .models import Client
import bcrypt


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'lastname', 'email', 'phone', 'image', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'image': {'required': False, 'allow_null': True, 'allow_blank': True}  # ✅ Imagen opcional
        }

    def create(self, validated_data):
        # Extraer y hashear la contraseña
        raw_password = validated_data.pop('password')
        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())
        validated_data['password'] = hashed_password.decode('utf-8')
        
        # Crear el cliente
        client = Client.objects.create(**validated_data)
        return client

    def update(self, instance, validated_data):
        # Si se incluye una nueva contraseña, hashearla
        if 'password' in validated_data:
            raw_password = validated_data.pop('password')
            hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())
            instance.password = hashed_password.decode('utf-8')
        
        # Actualizar los demás campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
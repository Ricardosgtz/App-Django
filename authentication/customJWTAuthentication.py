from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from clients.models import Client


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            client_id = validated_token['id']  # 👈 coincide con tu token personalizado
        except KeyError:
            raise AuthenticationFailed('Token no contiene un ID válido')

        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            raise AuthenticationFailed('Cliente no encontrado')

        client.is_authenticated = True
        return client

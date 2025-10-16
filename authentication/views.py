from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from clients.models import Client
from clients.serializers import ClientSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
import bcrypt


# -------------------------------
# 🟢 REGISTRO DE CLIENTES
# -------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = ClientSerializer(data=request.data)

    if serializer.is_valid():
        client = serializer.save()

        # 🎟️ Generar tokens JWT personalizados
        refresh_token = getCustomTokenForClient(client)
        access_token = str(refresh_token.access_token)

        response_data = {
            "cliente": {
                "id": client.id,
                "name": client.name,
                "lastname": client.lastname,
                "email": client.email,
                "phone": client.phone,
                "image": client.image if client.image else None,
            },
            "token": "Bearer " + access_token,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    # ❌ Manejo de errores de validación
    error_messages = [
        f"{field}: {', '.join(errors)}"
        for field, errors in serializer.errors.items()
    ]
    return Response(
        {"message": error_messages, "statusCode": 400},
        status=status.HTTP_400_BAD_REQUEST
    )


# -------------------------------
# 🪙 FUNCIÓN PARA CREAR TOKEN JWT
# -------------------------------
def getCustomTokenForClient(client):
    refresh_token = RefreshToken.for_user(client)
    refresh_token.payload['id'] = client.id
    refresh_token.payload['name'] = client.name
    refresh_token.payload['email'] = client.email
    return refresh_token


# -------------------------------
# 🔐 LOGIN DE CLIENTES
# -------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {"message": "El email y la contraseña son requeridos", "statusCode": 400},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        client = Client.objects.get(email__iexact=email)
    except Client.DoesNotExist:
        return Response(
            {"message": "El email o la contraseña no son válidos", "statusCode": 401},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # 🧠 Verificamos la contraseña con bcrypt
    try:
        if not bcrypt.checkpw(password.encode('utf-8'), client.password.encode('utf-8')):
            return Response(
                {"message": "El email o la contraseña no son válidos", "statusCode": 401},
                status=status.HTTP_401_UNAUTHORIZED
            )
    except Exception as e:
        return Response(
            {"message": f"Error interno: {str(e)}", "statusCode": 500},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # ✅ Generar token JWT
    refresh_token = getCustomTokenForClient(client)
    access_token = str(refresh_token.access_token)

    # 🖼️ La imagen ya viene con URL completa de Cloudinary
    # No necesitamos concatenar base_url
    client_data = {
        "cliente": {
            "id": client.id,
            "name": client.name,
            "lastname": client.lastname,
            "email": client.email,
            "phone": client.phone,
            "image": client.image if client.image else None,  # ✅ URL completa de Cloudinary
        },
        "token": "Bearer " + access_token,
    }

    return Response(client_data, status=status.HTTP_200_OK)
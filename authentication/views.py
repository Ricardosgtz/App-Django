from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from clients.models import Client
from clients.serializers import ClientSerializer
from rest_framework_simplejwt.tokens import RefreshToken
import bcrypt
from rest_framework.permissions import AllowAny
# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = ClientSerializer(data=request.data)
    if serializer.is_valid():
        client = serializer.save()
         # Generamos los tokens personalizados
        refresh_token = getCustoSTokenForClient(client)
        acceso_token = str(refresh_token.access_token)

        response_data = {
            "cliente": serializer.data,
            "token": "Bearer " + acceso_token,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    error_messages = []
    for field, errors in serializer.errors.items():
        for error in errors:
            error_messages.append(f"{field}: {error}")
    
    error_response = {
        "message": error_messages,
        "statusCode": status.HTTP_400_BAD_REQUEST
    }

    return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
    
# Función para generar token personalizado
def getCustoSTokenForClient(client):
    refresh_token = RefreshToken.for_user(client)
    del refresh_token.payload['user_id']  # Eliminamos el user_id por defecto
    refresh_token.payload['id'] = client.id
    refresh_token.payload['name'] = client.name
    return refresh_token


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {
                "message": "El email y el password son requeridos",
                "statusCode": status.HTTP_400_BAD_REQUEST
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Primero buscamos ignorando mayúsculas/minúsculas
        client = Client.objects.get(email__iexact=email)

        # 🔒 Validamos que el email coincida EXACTAMENTE
        if client.email != email:
            raise Client.DoesNotExist

    except Client.DoesNotExist:
        return Response(
            {
                "message": "El email o el password no son válidos",
                "statusCode": status.HTTP_401_UNAUTHORIZED
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Validamos contraseña
    if bcrypt.checkpw(password.encode("utf-8"), client.password.encode("utf-8")):
        refresh_token = getCustoSTokenForClient(client)
        access_token = str(refresh_token.access_token)
        client_data = {
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
        return Response(client_data, status=status.HTTP_200_OK)
    else:
        return Response(
            {
                "message": "El email o el password no son válidos",
                "statusCode": status.HTTP_401_UNAUTHORIZED
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

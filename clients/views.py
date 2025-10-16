from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Client


# 🧩 Función auxiliar para obtener URL base según entorno
def get_base_url():
    if settings.DEBUG:
        # 🌐 Modo local
        return "http://192.168.100.13:3000"
    else:
        # 🌐 Producción en Render
        return "https://app-django-86x6.onrender.com"


# 🟢 OBTENER CLIENTE POR ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_by_id(request, id_client):
    try:
        client = Client.objects.get(id=id_client)
    except Client.DoesNotExist:
        return Response({
            "message": "El cliente no existe",
            "statusCode": status.HTTP_404_NOT_FOUND
        }, status=status.HTTP_404_NOT_FOUND)

    base_url = get_base_url()
    client_data = {
        "id": client.id,
        "name": client.name,
        "lastname": client.lastname,
        "email": client.email,
        "phone": client.phone,
        "image": f"{base_url}{client.image}" if client.image else None,
    }
    return Response(client_data, status=status.HTTP_200_OK)


# 🟡 OBTENER TODOS LOS CLIENTES
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_users(request):
    clients = Client.objects.all()
    base_url = get_base_url()
    all_clients_data = []

    for client in clients:
        client_data = {
            "id": client.id,
            "name": client.name,
            "lastname": client.lastname,
            "email": client.email,
            "phone": client.phone,
            "image": f"{base_url}{client.image}" if client.image else None,
        }
        all_clients_data.append(client_data)

    return Response(all_clients_data, status=status.HTTP_200_OK)


# 🟣 ACTUALIZAR CLIENTE SIN IMAGEN
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update(request, id_client):
    if str(request.user.id) != str(id_client):
        return Response(
            {"message": "No tienes permiso para actualizar este cliente"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        client = Client.objects.get(id=id_client)
    except Client.DoesNotExist:
        return Response(
            {"message": "El cliente no existe"},
            status=status.HTTP_404_NOT_FOUND
        )

    name = request.data.get('name')
    lastname = request.data.get('lastname')
    phone = request.data.get('phone')

    if not any([name, lastname, phone]):
        return Response(
            {"message": "No se enviaron datos para actualizar"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if name:
        client.name = name
    if lastname:
        client.lastname = lastname
    if phone:
        client.phone = phone

    client.save()

    base_url = get_base_url()
    client_data = {
        "id": client.id,
        "name": client.name,
        "lastname": client.lastname,
        "email": client.email,
        "phone": client.phone,
        "image": f"{base_url}{client.image}" if client.image else None,
    }
    return Response(client_data, status=status.HTTP_200_OK)


# 🔵 ACTUALIZAR CLIENTE CON IMAGEN
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateWithImage(request, id_client):
    if str(request.user.id) != str(id_client):
        return Response(
            {"message": "No tienes permiso para actualizar este cliente"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        client = Client.objects.get(id=id_client)
    except Client.DoesNotExist:
        return Response(
            {"message": "El cliente no existe"},
            status=status.HTTP_404_NOT_FOUND
        )

    name = request.data.get('name')
    lastname = request.data.get('lastname')
    phone = request.data.get('phone')
    image = request.FILES.get('file')

    if not any([name, lastname, phone, image]):
        return Response(
            {"message": "No se enviaron datos para actualizar"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if name:
        client.name = name
    if lastname:
        client.lastname = lastname
    if phone:
        client.phone = phone
    if image:
        file_path = f'uploads/clients/{client.id}/{image.name}'
        saved_path = default_storage.save(file_path, ContentFile(image.read()))
        client.image = default_storage.url(saved_path)

    client.save()

    base_url = get_base_url()
    client_data = {
        "id": client.id,
        "name": client.name,
        "lastname": client.lastname,
        "email": client.email,
        "phone": client.phone,
        "image": f"{base_url}{client.image}" if client.image else None,
    }

    return Response(client_data, status=status.HTTP_200_OK)

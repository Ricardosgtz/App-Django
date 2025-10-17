from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from rest_framework import status
from .models import Client
import json


# ✅ Obtener cliente por ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_by_id(request, id_client):
    try:
        client = Client.objects.get(id=id_client)
    except Client.DoesNotExist:
        return Response(
            {"message": "El cliente no existe", "statusCode": status.HTTP_404_NOT_FOUND},
            status=status.HTTP_404_NOT_FOUND
        )

    # 🔗 Generar URL de imagen (Render o local)
    image_url = (
        f"https://{settings.RENDER_EXTERNAL_HOSTNAME}{client.image}"
        if not settings.DEBUG and client.image
        else f"http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{client.image}" if client.image else None
    )

    client_data = {
        "id": client.id,
        "name": client.name,
        "lastname": client.lastname,
        "email": client.email,
        "phone": client.phone,
        "image": image_url,
    }
    return Response(client_data, status=status.HTTP_200_OK)


# ✅ Obtener todos los clientes
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_users(request):
    clients = Client.objects.all()
    all_clients_data = []

    for client in clients:
        image_url = (
            f"https://{settings.RENDER_EXTERNAL_HOSTNAME}{client.image}"
            if not settings.DEBUG and client.image
            else f"http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{client.image}" if client.image else None
        )

        client_data = {
            "id": client.id,
            "name": client.name,
            "lastname": client.lastname,
            "email": client.email,
            "phone": client.phone,
            "image": image_url,
        }
        all_clients_data.append(client_data)

    return Response(all_clients_data, status=status.HTTP_200_OK)


# ✅ Actualizar cliente (sin imagen)
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
        return Response({"message": "El cliente no existe"}, status=status.HTTP_404_NOT_FOUND)

    name = request.data.get('name')
    lastname = request.data.get('lastname')
    phone = request.data.get('phone')

    if not any([name, lastname, phone]):
        return Response(
            {"message": "No se enviaron datos para actualizar"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if name: client.name = name
    if lastname: client.lastname = lastname
    if phone: client.phone = phone

    client.save()

    image_url = (
        f"https://{settings.RENDER_EXTERNAL_HOSTNAME}{client.image}"
        if not settings.DEBUG and client.image
        else f"http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{client.image}" if client.image else None
    )

    client_data = {
        "id": client.id,
        "name": client.name,
        "lastname": client.lastname,
        "email": client.email,
        "phone": client.phone,
        "image": image_url,
    }
    return Response(client_data, status=status.HTTP_200_OK)


# ✅ Actualizar cliente CON imagen
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
        return Response({"message": "El cliente no existe"}, status=status.HTTP_404_NOT_FOUND)

    # 🧩 Si Flutter envía 'user' en JSON, decodificarlo
    user_data = request.data.get('user')
    if user_data:
        try:
            user_data = json.loads(user_data)
        except json.JSONDecodeError:
            user_data = {}

    name = user_data.get('name') if isinstance(user_data, dict) else request.data.get('name')
    lastname = user_data.get('lastname') if isinstance(user_data, dict) else request.data.get('lastname')
    phone = user_data.get('phone') if isinstance(user_data, dict) else request.data.get('phone')
    image = request.FILES.get('file')

    if not any([name, lastname, phone, image]):
        return Response(
            {"message": "No se enviaron datos para actualizar"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 📸 Guardar imagen si se envía
    if image:
        file_path = f'uploads/clients/{client.id}/{image.name}'
        saved_path = default_storage.save(file_path, ContentFile(image.read()))
        client.image = default_storage.url(saved_path)

    if name: client.name = name
    if lastname: client.lastname = lastname
    if phone: client.phone = phone

    client.save()

    image_url = (
        f"https://{settings.RENDER_EXTERNAL_HOSTNAME}{client.image}"
        if not settings.DEBUG and client.image
        else f"http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{client.image}" if client.image else None
    )

    client_data = {
        "id": client.id,
        "name": client.name,
        "lastname": client.lastname,
        "email": client.email,
        "phone": client.phone,
        "image": image_url,
    }

    return Response(client_data, status=status.HTTP_200_OK)

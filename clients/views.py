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
from MyDjangoProjectServer.supabase_client import upload_file_to_supabase


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_by_id(request, id_client):
    try:
        client = Client.objects.get(id=id_client)
    except Client.DoesNotExist:
        return Response(
            {"message": "El cliente no existe"},
            status=status.HTTP_404_NOT_FOUND
        )

    client_data = {
        "id": client.id,
        "name": client.name,
        "lastname": client.lastname,
        "email": client.email,
        "phone": client.phone,
        "image": client.image  # ✅ ya es la URL completa de Supabase
    }
    return Response(client_data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_users(request):
    clients = Client.objects.all()
    all_clients_data = []

    for client in clients:
        client_data = {
            "id": client.id,
            "name": client.name,
            "lastname": client.lastname,
            "email": client.email,
            "phone": client.phone,
            "image": client.image  # ✅ ya es URL pública
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

    client_data = {
        "id": client.id,
        "name": client.name,
        "lastname": client.lastname,
        "email": client.email,
        "phone": client.phone,
        "image": client.image  # ✅ URL completa
    }
    return Response(client_data, status=status.HTTP_200_OK)


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

    # Subir imagen a Supabase si se envió
    if image:
        try:
            public_url = upload_file_to_supabase(image, client.id)
            client.image = public_url
        except Exception as e:
            return Response(
                {"message": f"Error al subir imagen: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    client.save()

    client_data = {
        "id": client.id,
        "name": client.name,
        "lastname": client.lastname,
        "email": client.email,
        "phone": client.phone,
        "image": client.image,
    }

    return Response(client_data, status=status.HTTP_200_OK)


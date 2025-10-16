from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from rest_framework import status
from .models import Client
from django.views.decorators.csrf import csrf_exempt
import json


# 🌍 Helper para construir URLs de imagen seguras
def build_image_url(request, image_field):
    if not image_field:
        return None
    # genera una URL completa y accesible (Render o local)
    return request.build_absolute_uri(image_field.url)


# 🟩 OBTENER CLIENTE POR ID
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_by_id(request, id_client):
    try:
        client = Client.objects.get(id=id_client)
    except Client.DoesNotExist:
        return Response({
            "message": "El cliente no existe",
            "statusCode": 404
        }, status=status.HTTP_404_NOT_FOUND)

    client_data = {
        "id": client.id,
        "name": client.name,
        "lastname": client.lastname,
        "email": client.email,
        "phone": client.phone,
        "image": build_image_url(request, client.image)
    }
    return Response(client_data, status=status.HTTP_200_OK)


# 🟦 OBTENER TODOS LOS CLIENTES
@csrf_exempt
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
            "image": build_image_url(request, client.image)
        }
        all_clients_data.append(client_data)

    return Response(all_clients_data, status=status.HTTP_200_OK)


# 🟩 ACTUALIZAR CLIENTE (sin imagen)
@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update(request, id_client):
    if str(request.user.id) != str(id_client):
        return Response(
            {"message": "No tienes permiso para actualizar este cliente", "statusCode": 403},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        client = Client.objects.get(id=id_client)
    except Client.DoesNotExist:
        return Response(
            {"message": "El cliente no existe", "statusCode": 404},
            status=status.HTTP_404_NOT_FOUND
        )

    name = request.data.get('name')
    lastname = request.data.get('lastname')
    phone = request.data.get('phone')

    if not any([name, lastname, phone]):
        return Response(
            {"message": "No se enviaron datos para actualizar", "statusCode": 400},
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
        "image": build_image_url(request, client.image)
    }

    return Response(client_data, status=status.HTTP_200_OK)


# 🟦 ACTUALIZAR CLIENTE CON IMAGEN
@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateWithImage(request, id_client):
    if str(request.user.id) != str(id_client):
        return Response(
            {"message": "No tienes permiso para actualizar este cliente", "statusCode": 403},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        client = Client.objects.get(id=id_client)
    except Client.DoesNotExist:
        return Response(
            {"message": "El cliente no existe", "statusCode": 404},
            status=status.HTTP_404_NOT_FOUND
        )

    # Si Flutter manda 'user' como JSON dentro del form-data:
    if 'user' in request.data:
        try:
            user_data = json.loads(request.data['user'])
            name = user_data.get('name')
            lastname = user_data.get('lastname')
            phone = user_data.get('phone')
        except:
            name = request.data.get('name')
            lastname = request.data.get('lastname')
            phone = request.data.get('phone')
    else:
        name = request.data.get('name')
        lastname = request.data.get('lastname')
        phone = request.data.get('phone')

    image = request.FILES.get('file')

    if not any([name, lastname, phone, image]):
        return Response(
            {"message": "No se enviaron datos para actualizar", "statusCode": 400},
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

    client_data = {
        "id": client.id,
        "name": client.name,
        "lastname": client.lastname,
        "email": client.email,
        "phone": client.phone,
        "image": build_image_url(request, client.image)
    }

    return Response({
        "message": "Perfil actualizado correctamente",
        "client": client_data
    }, status=status.HTTP_200_OK)

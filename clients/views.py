from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.base import ContentFile
from django.conf import settings
from rest_framework import status
from .models import Client


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_by_id(request, id_client):
    try:
        client = Client.objects.get(id=id_client)
    except Client.DoesNotExist:
        return Response(
            {
                "message": "El cliente no existe",
                "statusCode": status.HTTP_404_NOT_FOUND
            },
            status=status.HTTP_404_NOT_FOUND
        )

    client_data = {
        "id": client.id,
        "name": client.name,
        "lastname": client.lastname,
        "email": client.email,
        "phone": client.phone,
        "image": f'http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{client.image}' if client.image else None,
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
            "image": f'http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{client.image}' if client.image else None,
        }
        all_clients_data.append(client_data)

    return Response(all_clients_data, status=status.HTTP_200_OK)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update(request, id_client):
    if str(request.user.id) != str(id_client):
        return Response(
            {
                "message": "No tienes permiso para actualizar este cliente",
                "statusCode": status.HTTP_403_FORBIDDEN
            },
            status=status.HTTP_403_FORBIDDEN
        )
    try:
        client = Client.objects.get(id=id_client)
    except Client.DoesNotExist:
        return Response(
            {
                "message": "El cliente no existe",
                "statusCode": status.HTTP_404_NOT_FOUND
            },
            status=status.HTTP_404_NOT_FOUND
        )

    name = request.data.get('name', None)
    lastname = request.data.get('lastname', None)
    phone = request.data.get('phone', None)

    if name is None and lastname is None and phone is None:
        return Response(
            {
                "message": "No se enviaron datos para actualizar",
                "statusCode": status.HTTP_400_BAD_REQUEST
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if name is not None:
        client.name = name
    if lastname is not None:
        client.lastname = lastname
    if phone is not None:
        client.phone = phone

    client.save()

    client_data = {
        "id": client.id,
        "name": client.name,
        "lastname": client.lastname,
        "email": client.email,
        "phone": client.phone,
        "image": f'http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{client.image}' if client.image else None,
    }
    return Response(client_data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateWithImage(request, id_client):
    if str(request.user.id) != str(id_client):
        return Response(
            {
                "message": "No tienes permiso para actualizar este cliente",
                "statusCode": status.HTTP_403_FORBIDDEN
            },
            status=status.HTTP_403_FORBIDDEN
        )
    try:
        client = Client.objects.get(id=id_client)
    except Client.DoesNotExist:
        return Response(
            {
                "message": "El cliente no existe",
                "statusCode": status.HTTP_404_NOT_FOUND
            },
            status=status.HTTP_404_NOT_FOUND
        )

    name = request.data.get('name', None)
    lastname = request.data.get('lastname', None)
    phone = request.data.get('phone', None)
    image = request.FILES.get('file', None)

    if name is None and lastname is None and phone is None and image is None:
        return Response(
            {
                "message": "No se enviaron datos para actualizar",
                "statusCode": status.HTTP_400_BAD_REQUEST
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if name is not None:
        client.name = name
    if lastname is not None:
        client.lastname = lastname
    if phone is not None:
        client.phone = phone
    if image is not None:
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
        "image": f'http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{client.image}' if client.image else None,
    }
    return Response(client_data, status=status.HTTP_200_OK)
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Client
import cloudinary.uploader


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_by_id(request, id_client):
    """
    Obtener un cliente por ID
    """
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
        "image": client.image if client.image else None,
    }
    return Response(client_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_users(request):
    """
    Obtener todos los clientes
    """
    clients = Client.objects.all()
    all_clients_data = []

    for client in clients:
        client_data = {
            "id": client.id,
            "name": client.name,
            "lastname": client.lastname,
            "email": client.email,
            "phone": client.phone,
            "image": client.image if client.image else None,
        }
        all_clients_data.append(client_data)

    return Response(all_clients_data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update(request, id_client):
    """
    Actualizar cliente sin imagen
    """
    try:
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
            "image": client.image if client.image else None,
        }
        return Response(client_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {
                "message": f"Error al actualizar: {str(e)}",
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateWithImage(request, id_client):
    """
    Actualizar cliente con imagen usando Cloudinary
    """
    try:
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
        
        # Actualizar campos de texto
        if name is not None:
            client.name = name
        if lastname is not None:
            client.lastname = lastname
        if phone is not None:
            client.phone = phone
        
        # Subir imagen a Cloudinary
        if image is not None:
            try:
                # Subir a Cloudinary
                upload_result = cloudinary.uploader.upload(
                    image,
                    folder=f"clients/{client.id}",
                    resource_type="auto",
                    overwrite=True,
                    invalidate=True
                )
                
                # Guardar la URL segura de Cloudinary
                client.image = upload_result['secure_url']
                
            except Exception as upload_error:
                return Response(
                    {
                        "message": f"Error al subir imagen: {str(upload_error)}",
                        "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        client.save()

        client_data = {
            "id": client.id,
            "name": client.name,
            "lastname": client.lastname,
            "email": client.email,
            "phone": client.phone,
            "image": client.image if client.image else None,
        }
        return Response(client_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {
                "message": f"Error al actualizar: {str(e)}",
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
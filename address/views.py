from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from address.models import Address
from address.serializers import AddressSerializer

def format_serializer_errors(errors):
    """Convierte los errores del serializer en una lista de strings"""
    error_messages = []
    for field, errs in errors.items():
        for err in errs:
            error_messages.append(f"{field}: {err}")
    return error_messages

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create(request):
    serializer = AddressSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            "message": format_serializer_errors(serializer.errors),
            "statusCode": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_address_by_user(request, id_client):
    try:
        # ✅ Buscar correctamente por el cliente (ForeignKey)
        addresses = Address.objects.filter(client_id=id_client)
        serializer = AddressSerializer(addresses, many=True)
        
        # ✅ Devuelve lista vacía [] si no hay direcciones
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'message': f'Error al obtener las direcciones: {str(e)}',
            'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete(request, id_address):
    try:
        address = Address.objects.get(id=id_address)
        address.delete()
        return Response(True, status=status.HTTP_200_OK)
    except Address.DoesNotExist:
        return Response({
            'message': 'La dirección no existe',
            'statusCode': status.HTTP_404_NOT_FOUND
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update(request, id_address):
    try:
        address = Address.objects.get(id=id_address)
    except Address.DoesNotExist:
        return Response({
            'message': 'La dirección no existe',
            'statusCode': status.HTTP_404_NOT_FOUND
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = AddressSerializer(address, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response({
            "message": format_serializer_errors(serializer.errors),
            "statusCode": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)
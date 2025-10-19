# orders/views.py
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from orders.models import Order, OrderDetail
from orders.serializers import (
    OrderCreateSerializer, 
    OrderListSerializer, 
    OrderRetrieveSerializer
)
from products.models import Product

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """Crea una nueva orden con sus detalles y la envía por WebSocket."""
    serializer = OrderCreateSerializer(data=request.data, context={'request': request})

    if not serializer.is_valid():
        error_messages = []
        for field, errors in serializer.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")

        error_response = {
            "message": error_messages,
            "statusCode": status.HTTP_400_BAD_REQUEST
        }
        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

    try:
        # ✅ Guardar la orden
        order = serializer.save()

        # ✅ Serializar para respuesta HTTP y para WebSocket
        response_serializer = OrderRetrieveSerializer(order)
        order_data = response_serializer.data  # datos limpios listos para enviar

        # ✅ Enviar mensaje por WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "orders_group",  # nombre del grupo en el consumer
            {
                "type": "send_new_order",
                "data": {
                    "message": "🆕 Nueva orden creada",
                    "order": order_data
                }
            }
        )

        # ✅ Responder al cliente (Flutter)
        return Response(order_data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {
                "message": f'Error al crear la orden: {str(e)}',
                "statusCode": status.HTTP_400_BAD_REQUEST
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders_by_client(request, client_id):
    """Obtiene todas las órdenes de un cliente específico"""
    try:
        orders = Order.objects.filter(client_id=client_id)
        
        if not orders.exists():
            return Response(
                {
                    "message": "No tienes órdenes",
                    "statusCode": status.HTTP_404_NOT_FOUND,
                    "data": []
                }, 
                status=status.HTTP_200_OK
            )
        
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {
                "message": f'Error al obtener las órdenes: {str(e)}',
                "statusCode": status.HTTP_400_BAD_REQUEST
            }, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_detail(request, order_id):
    """Obtiene el detalle completo de una orden específica"""
    try:
        order = Order.objects.get(id=order_id)
        serializer = OrderRetrieveSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Order.DoesNotExist:
        return Response(
            {
                "message": 'La orden no existe',
                "statusCode": status.HTTP_404_NOT_FOUND
            }, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {
                "message": f'Error al obtener la orden: {str(e)}',
                "statusCode": status.HTTP_400_BAD_REQUEST
            }, 
            status=status.HTTP_400_BAD_REQUEST
        )
    


# --- PRUEBA WEBSOCKET ---

@api_view(['GET'])
def test_ws(request):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "orders_group",
        {
            "type": "send_new_order",
            "data": {
                "message": "🔥 WebSocket funcionando correctamente desde el backend (Render + Railway)!",
                "status": "success"
            }
        }
    )
    return Response({"message": "Mensaje enviado al WebSocket"})

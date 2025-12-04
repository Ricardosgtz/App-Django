# payments/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from payments.models import Payment
from payments.serializers import PaymentSerializer
from orders.models import Order
from django.utils import timezone
from MyDjangoProjectServer.supabase_client import upload_comprobante_to_supabase


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    """
    Crea un pago. Calcula automáticamente el total incluyendo cargo de envío.
    """
    try:
        order_id = request.data.get('order_id')
        payment_method = request.data.get('payment_method')
        comprobante = request.FILES.get('comprobante')

        if not order_id:
            return Response(
                {"message": "El campo 'order_id' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar la orden
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"message": "La orden especificada no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        client_id = order.client.id

        # Validar método de pago
        if payment_method not in ['efectivo', 'transferencia']:
            return Response(
                {"message": "Método de pago inválido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Si es transferencia, validar comprobante
        public_url = None
        if payment_method == 'transferencia':
            if not comprobante:
                return Response(
                    {"message": "Debes subir el comprobante."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            public_url = upload_comprobante_to_supabase(comprobante, client_id)

        try:
            subtotal = float(order.get_total() or 0)
            delivery_fee = 15.0 if order.order_type == 'domicilio' else 0.0
            total_amount = subtotal + delivery_fee
        except Exception as calc_error:
            print(f"❌ Error en cálculo: {calc_error}")
            return Response(
                {"message": f"Error al calcular el total: {str(calc_error)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            status='pendiente',
            amount=total_amount,
            receipt=public_url,
            payment_date=timezone.now(),
        )

        serializer = PaymentSerializer(payment)
        return Response({
            "message": "Pago registrado correctamente",
            "statusCode": 201,
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        import traceback
        print("❌ Error completo en create_payment:")
        print(traceback.format_exc())
        
        return Response(
            {"message": f"Error al crear el pago: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_by_order(request, order_id):
    """
    Obtiene el pago asociado a una orden específica.
    """
    try:
        # Buscar la orden
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"message": "La orden especificada no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verificar que el usuario autenticado sea el dueño de la orden
        if order.client.id != request.user.id:
            return Response(
                {"message": "No tienes permiso para ver el pago de esta orden."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Buscar el pago asociado a la orden
        try:
            payment = Payment.objects.get(order=order)
            serializer = PaymentSerializer(payment)
            return Response({
                "message": "Pago obtenido correctamente",
                "statusCode": 200,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response(
                {"message": "No se encontró un pago para esta orden."},
                status=status.HTTP_404_NOT_FOUND
            )

    except Exception as e:
        print("❌ Error en get_payment_by_order:", e)
        return Response(
            {"message": f"Error al obtener el pago: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
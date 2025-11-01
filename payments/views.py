# payments/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from payments.models import Payment
from payments.serializers import PaymentSerializer
from orders.models import Order
from MyDjangoProjectServer.supabase_client import upload_comprobante_to_supabase  # ✅ Import directo

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    """
    📥 Crea un pago. Si es por transferencia, sube el comprobante a Supabase.
    """
    try:
        order_id = request.data.get('order_id')
        payment_method = request.data.get('payment_method')
        comprobante = request.FILES.get('comprobante')

        if not order_id:
            return Response(
                {"message": "La orden es obligatoria."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"message": "La orden no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        client_id = order.client.id  # ✅ Usamos el id del cliente de la orden

        # 🔸 Validar método
        if payment_method not in ['efectivo', 'transferencia']:
            return Response(
                {"message": "Método de pago inválido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔸 Validar comprobante si es transferencia
        public_url = None
        if payment_method == 'transferencia':
            if not comprobante:
                return Response(
                    {"message": "Debes subir el comprobante para pagos por transferencia."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ✅ Subir a Supabase
            public_url = upload_comprobante_to_supabase(comprobante, client_id)

        # ✅ Crear pago
        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            status='pendiente',
            amount=order.get_total(),  # Monto igual al total de la orden
            receipt=public_url
        )

        serializer = PaymentSerializer(payment)
        return Response({
            "message": "Pago registrado correctamente",
            "statusCode": 201,
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {"message": f"Error al subir comprobante: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

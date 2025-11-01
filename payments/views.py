from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from payments.models import Payment
from payments.serializers import PaymentSerializer
from orders.models import Order


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_payment(request):
    """
    📤 Crea un nuevo pago (efectivo o transferencia).
    - El cliente **no envía monto ni estatus**.
    - Si es transferencia, debe subir el comprobante.
    - El monto se toma del total de la orden.
    - El estatus inicia como 'pendiente'.
    """
    try:
        payment_method = request.data.get('payment_method')
        order_id = request.data.get('order_id')
        comprobante = request.FILES.get('receipt')

        if not payment_method:
            return Response({"message": "El método de pago es obligatorio."}, status=400)
        if not order_id:
            return Response({"message": "La orden es obligatoria."}, status=400)

        # ✅ Buscar la orden
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"message": "La orden no existe."}, status=404)

        # ✅ Crear el pago base
        payment = Payment(
            order=order,
            payment_method=payment_method,
            status='pendiente',
            amount=order.get_total()
        )

        # 🧾 Si el método es transferencia → requiere comprobante
        if payment_method == 'transferencia':
            if not comprobante:
                return Response(
                    {"message": "Debes subir el comprobante para pagos por transferencia."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                client = getattr(request.user, 'client', None)
                client_id = client.id if client else request.user.id
                # 📤 Sube el comprobante a Supabase en: Comprobantes/{client_id}/archivo.jpg
                public_url = settings.upload_comprobante_to_supabase(comprobante, client_id)
                payment.receipt = public_url
            except Exception as e:
                return Response(
                    {"message": f"Error al subir comprobante: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        payment.save()

        serializer = PaymentSerializer(payment, context={'request': request})
        return Response({
            "message": "Pago registrado correctamente",
            "statusCode": 201,
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        print("❌ Error al crear pago:", e)
        return Response({
            "message": f"Error al crear pago: {str(e)}",
            "statusCode": 400
        }, status=status.HTTP_400_BAD_REQUEST)

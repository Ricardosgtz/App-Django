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
from MyDjangoProjectServer.supabase_client import upload_comprobante_to_supabase  # ✅ Import directo


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    """
    📥 Crea un pago. Calcula automáticamente el total incluyendo cargo de envío.
    """
    print("="*60)
    print("🚀 INICIO DE create_payment")
    print("="*60)
    
    try:
        order_id = request.data.get('order_id')
        payment_method = request.data.get('payment_method')
        comprobante = request.FILES.get('comprobante')

        print(f"📦 Datos recibidos:")
        print(f"   - order_id: {order_id}")
        print(f"   - payment_method: {payment_method}")
        print(f"   - comprobante: {comprobante}")

        if not order_id:
            print("❌ Falta order_id")
            return Response(
                {"message": "El campo 'order_id' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔎 Buscar la orden
        print(f"🔍 Buscando orden ID: {order_id}")
        try:
            order = Order.objects.get(id=order_id)
            print(f"✅ Orden encontrada: {order.id}")
            print(f"   - Tipo de orden: {order.order_type}")
            print(f"   - Cliente: {order.client.id}")
        except Order.DoesNotExist:
            print(f"❌ Orden {order_id} no existe")
            return Response(
                {"message": "La orden especificada no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        client_id = order.client.id

        # 🔸 Validar método de pago
        print(f"💳 Validando método de pago: {payment_method}")
        if payment_method not in ['efectivo', 'transferencia']:
            print(f"❌ Método inválido: {payment_method}")
            return Response(
                {"message": "Método de pago inválido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔸 Si es transferencia, validar comprobante
        public_url = None
        if payment_method == 'transferencia':
            print("📤 Es transferencia, validando comprobante...")
            if not comprobante:
                print("❌ Falta comprobante")
                return Response(
                    {"message": "Debes subir el comprobante."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            print("☁️ Subiendo a Supabase...")
            try:
                public_url = upload_comprobante_to_supabase(comprobante, client_id)
                print(f"✅ Subido correctamente: {public_url}")
            except Exception as supabase_error:
                print(f"❌ Error en Supabase: {supabase_error}")
                import traceback
                traceback.print_exc()
                return Response(
                    {"message": f"Error al subir comprobante: {str(supabase_error)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            print("💵 Es efectivo, no se requiere comprobante")

        # Calcular total
        print("🧮 Calculando total...")
        try:
            print(f"   Llamando a order.get_total()...")
            raw_total = order.get_total()
            print(f"   Resultado: {raw_total} (tipo: {type(raw_total)})")
            
            subtotal = float(raw_total or 0)
            print(f"   Subtotal: ${subtotal}")
            
            delivery_fee = 15.0 if order.order_type == 'domicilio' else 0.0
            print(f"   Cargo envío: ${delivery_fee}")
            
            total_amount = subtotal + delivery_fee
            print(f"   💰 TOTAL: ${total_amount}")
            
        except Exception as calc_error:
            print(f"❌ Error en cálculo: {calc_error}")
            import traceback
            traceback.print_exc()
            return Response(
                {"message": f"Error al calcular el total: {str(calc_error)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Crear el pago
        print("💾 Creando Payment en la BD...")
        print(f"   - order: {order.id}")
        print(f"   - payment_method: {payment_method}")
        print(f"   - status: pendiente")
        print(f"   - amount: {total_amount}")
        print(f"   - receipt: {public_url}")
        
        try:
            payment = Payment.objects.create(
                order=order,
                payment_method=payment_method,
                status='pendiente',
                amount=total_amount,
                receipt=public_url,
                payment_date=timezone.now(),
            )
            print(f"✅ Payment creado con ID: {payment.id}")
        except Exception as db_error:
            print(f"❌ Error al crear Payment: {db_error}")
            import traceback
            traceback.print_exc()
            raise

        print("📦 Serializando...")
        serializer = PaymentSerializer(payment)
        
        print("✅ TODO EXITOSO")
        print("="*60)
        
        return Response({
            "message": "Pago registrado correctamente",
            "statusCode": 201,
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        print("="*60)
        print(f"💥 ERROR GENERAL: {e}")
        print(f"   Tipo: {type(e).__name__}")
        import traceback
        print("📋 Traceback completo:")
        traceback.print_exc()
        print("="*60)
        
        return Response(
            {"message": f"Error al crear el pago: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_by_order(request, order_id):
    """
    📋 Obtiene el pago asociado a una orden específica.
    """
    try:
        # 🔎 Buscar la orden
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

        # 🔎 Buscar el pago asociado a la orden
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
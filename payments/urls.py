from django.urls import path
from .views import create_payment, get_payment_by_order

urlpatterns = [
    # 📤 Crear un nuevo pago (efectivo o transferencia)
    path('', create_payment ),
    path('/order/<int:order_id>/', get_payment_by_order),
]

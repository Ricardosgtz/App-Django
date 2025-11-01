from django.urls import path
from .views import create_payment

urlpatterns = [
    # 📤 Crear un nuevo pago (efectivo o transferencia)
    path('', create_payment ),
]

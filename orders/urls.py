# orders/urls.py
from django.urls import path
from .views import create_order, get_orders_by_client, get_order_detail

urlpatterns = [
    path('', create_order),
    path('/client/<client_id>', get_orders_by_client),
    path('/<order_id>', get_order_detail),
]
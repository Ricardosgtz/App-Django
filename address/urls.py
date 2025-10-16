from django.urls import path
from .views import create, get_address_by_user, delete, update
urlpatterns = [
    path('', create),
    path('/clients/<id_client>', get_address_by_user),
    path('/<id_address>', delete),    
    path('/update/<id_address>', update),
]
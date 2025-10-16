from django.urls import path
from .views import get_products_by_category
urlpatterns = [
    path('/category/<id_category>', get_products_by_category),
]
    
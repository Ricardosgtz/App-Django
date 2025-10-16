from django.urls import path
from .views import update, updateWithImage, get_user_by_id,get_all_users
urlpatterns = [
    path('/<id_client>', update),
    path('/findById/<id_client>', get_user_by_id),
    path('/', get_all_users),
    path('/upload/<id_client>', updateWithImage),
]
    
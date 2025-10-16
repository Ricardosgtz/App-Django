from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from categories.models import Category
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from categories.models import Category




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_categories(request):
    categories = Category.objects.all()
    all_categories_data = []

    for category in categories:
        category_data = {
            "id": category.id,
            "restaurant_id": category.id_restaurant.id if category.id_restaurant else None,
            "restaurant_name": category.id_restaurant.name if category.id_restaurant else None,
            "name": category.name,
            "description": category.description,
            "created_at": category.created_at,
            "updated_at": category.updated_at,
            "image": category.image if category.image else None,
            
        }
        all_categories_data.append(category_data)
    
    return Response(all_categories_data)
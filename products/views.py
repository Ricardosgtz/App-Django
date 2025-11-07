from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_products_by_category(request, id_category):
    """
    Obtiene todos los productos activos (no eliminados) de una categoría específica
    y devuelve un campo 'is_available' consistente para la app.
    """
    # Filtrar solo productos NO eliminados
    products = Product.objects.filter(id_category=id_category, deleted=False)
    
    if not products.exists():
        return Response({
            'message': 'No hay productos para esta categoría',
            'statusCode': status.HTTP_404_NOT_FOUND
        }, status=status.HTTP_404_NOT_FOUND)

    serialized_products = ProductSerializer(products, many=True).data
    return Response(serialized_products, status=status.HTTP_200_OK)
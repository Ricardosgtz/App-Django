from rest_framework import serializers
from categories.models import Category
from products.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'id_category', 'name', 'description', 'price',
            'image1', 'image2', 'created_at', 'updated_at', 'available'  # <-- agregado
        ]

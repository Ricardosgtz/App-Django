from rest_framework import serializers

from categories.models import Category

class CategorySerializer(serializers.ModelSerializer):
    file = serializers.ImageField(source='image', required=True)

    class Meta:
        model = Category
        fields = ['id', 'restaurant_id', 'restaurant_name', 'name', 'description', 'created_at', 'updated_at', 'file']
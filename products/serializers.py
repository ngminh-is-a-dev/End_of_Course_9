from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    roast_label = serializers.CharField(source='get_roast_level_display', read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='products-api:product-detail', lookup_field='slug')

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'url', 'category', 'category_slug', 'description', 'price', 'roast_level', 'roast_label', 'origin', 'stock', 'is_featured')

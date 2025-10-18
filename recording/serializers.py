from rest_framework import serializers
from .models import Category, SubCategory, Recording

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'subcategory']

class CategorySerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    subcategories = SubCategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'category', 'type', 'type_display', 'subcategories']

class RecordingSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_name = serializers.CharField(source='category.category', read_only=True)
    type_name = serializers.CharField(source='category.get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Recording
        fields = [
            'id', 'creation_date', 'status', 'status_display', 
            'category', 'category_name', 'type_name',
            'sum', 'comment'
        ]

class RecordingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recording
        fields = ['status', 'category', 'sum', 'comment']

class RecordingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recording
        fields = ['status', 'category', 'sum', 'comment']
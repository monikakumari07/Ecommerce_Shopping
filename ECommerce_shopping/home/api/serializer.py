from ..models import *
from rest_framework import serializers
from django.core.exceptions import ValidationError
from dateutil.parser import parse

class CustomUserSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ['otp']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductPictureSerializer(serializers.ModelSerializer):
	class Meta:
		model = ProductPicture
		fields = '__all__'
  
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()  # Nested serializer to represent the Category
    product_picture = ProductPictureSerializer(many=True, read_only=True)  # Nested serializer for studio_pictures
    class Meta:
        model = Product
        fields = '__all__'
        
    def get_category(self, obj):
        return str(obj.category)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['category'] = data['category'].split('of')[0].strip()
        return data  

    
    

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()  # Nested serializer for Product
    class Meta:
        model = CartItem
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()  # Nested serializer for Product
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer()  # Nested serializer for UserProfile
    products = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = '__all__'
        
class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status', 'order_status']
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..models import *
from .serializer import *
import random
from .custom_permissions import IsSuperAdmin

class ProductCreateAPI(APIView):
    # permission_classes =[IsAuthenticated,IsSuperAdmin]
    def get(self, request):
        product_get_all = Product.objects.all()
        serializer = ProductSerializer(product_get_all, many=True)
        print(serializer.data)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self,request):
        product_name = request.data.get('product_name')
        description = request.data.get('description')
        price = request.data.get('price')
        stock = request.data.get('stock')
        category = request.data.get('category')
        
        category_obj = Category.objects.get(pk=category)
        is_product = Product.objects.filter(product_name=request.data.get('product_name')).exists()
        if is_product :
            return Response({"message":"Already Register Enter another name "},status=status.HTTP_400_BAD_REQUEST)
        
        # Validate the "stock" field
        try:
            stock = int(stock)  # Attempt to convert to an integer
            if stock <= 0:
                raise ValueError("Stock must be a positive integer")
        except (ValueError, TypeError):
            return Response({"message": "Stock must be a positive integer"}, status=status.HTTP_400_BAD_REQUEST)

        product = Product.objects.create(
            product_name=product_name,
            description=description,
            price=price,
            stock=stock,
            category=category_obj,
                 
        )
        product_pictures = request.FILES.getlist('product_pictures', [])
        print(product_pictures)
        for pic in product_pictures:
            obj_pictures = ProductPicture.objects.create(
                product=product,
                product_picture=pic
            ) 
        
        product.save()
        serializer = ProductSerializer(product)
        return Response({"message":"sucessfully created","data":serializer.data},status=status.HTTP_201_CREATED )   

#Update the PRODUCT API
class ProductUpdateRetriveDeleteAPI(APIView):
    # permission_classes =[IsAuthenticated,IsSuperAdmin]
    def put(self,request,product_id):
        try:
            product = Product.objects.get(id=product_id)
        except UserDetail.DoesNotExist:
            return Response({"message": "Id does not exist"}, status=status.HTTP_400_BAD_REQUEST) 
              
        if Product.objects.filter(product_name=request.data.get('product_name')).exists():
            return Response({"message": "product name  already exist, please enter another name."}, status=status.HTTP_404_NOT_FOUND)
        
        product.product_name = request.data.get("product_name", product.product_name)
        product.description = request.data.get("description", product.description)
        product.price = request.data.get("price", product.price)
        product.stock = request.data.get("stock", product.stock)
        
#category updation        
        category_name = request.data.get('category')
        if category_name:
            try:
                category_obj = Category.objects.get(id=category_name)
                product.category = category_obj
            except Category.DoesNotExist:
                return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
            
#product picture Updation            
        product_pictures  = request.FILES.getlist('product_pictures', [])
        product.product_picture.all().delete()
        for pics in product_pictures:
                ProductPicture.objects.create(product=product, product_picture=pics)

        product.save()
        serializer = ProductSerializer(product)
        return Response({"message": "Successfully updated.", "data": serializer.data}, status=status.HTTP_200_OK)


#DELETE
    def delete(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"message": "product Id not found"}, status=status.HTTP_404_NOT_FOUND)
        product.delete()       
        return Response({"message": "product Id deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


#GET BY ID    
    def get(self, request,product_id):
            if product_id:
                get_by_product = Product.objects.get(id=product_id)
                serializer = ProductSerializer(get_by_product)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        
#CATEGORY API
class CategoryListCreate(generics.ListCreateAPIView):
    # permission_classes =[IsAuthenticated,IsSuperAdmin]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes =[IsAuthenticated,IsSuperAdmin]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer        

#CART APIS
class CartItemCreate(APIView):
    def get(self, request):
        cart_item_get_all = CartItem.objects.all()
        serializer = CartItemSerializer(cart_item_get_all, many=True)
        print(serializer.data)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)  # Default to 1 if not provided
        
        try:
            user = CustomUser.objects.get(pk=user_id)
            product = Product.objects.get(pk=product_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        cart_item = None
        # Check if a CartItem with the same user and product already exists
        existing_cart_item = CartItem.objects.filter(user=user, product=product).first()
        
        if existing_cart_item:
            # Update the quantity of the existing CartItem
            existing_cart_item.quantity += quantity
            existing_cart_item.save()
            cart_item = existing_cart_item
        else:
            # Create a new CartItem
            cart_item = CartItem(user=user, product=product, quantity=quantity)
            cart_item.save()
        
        serializer = CartItemSerializer(cart_item)  # Use the serializer to serialize the data
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
#UPDATE Cart Item
class CartItemUpdateRetrive(APIView):
    def put(self, request, cart_item_id):
        try:
            cart_item = CartItem.objects.get(id=cart_item_id)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)  # Default to 1 if not provided

        try:
            user = CustomUser.objects.get(pk=user_id)
            product = Product.objects.get(pk=product_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

       

        # Ensure the provided user and product match the cart_item's user and product
        if cart_item.user != user or cart_item.product != product:
            return Response({'error': 'Cart item does not match user and product'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the quantity of the CartItem
        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartItemSerializer(cart_item)  # Use the serializer to serialize the updated data
        return Response(serializer.data, status=status.HTTP_200_OK)
#DELETE
    def delete(self, request, cart_item_id):
        try:
            cart_item = Product.objects.get(id=cart_item_id)
        except Product.DoesNotExist:
            return Response({"message": "Cart item Id not found"}, status=status.HTTP_404_NOT_FOUND)
        cart_item.delete()       
        return Response({"message": "Cart item Id deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

#ORDER CREATE APIs
class OrderCreateAPI(APIView):
    def post(self, request, format=None):
        user_id = request.data.get('user_id')
        product_ids = request.data.get('product_ids', [])
        total_amount = request.data.get('total_amount')
        order_status = request.data.get('order_status')

        payment_status = request.data.get('payment_status', 'pending')

        if payment_status == 'cod':
            payment_status = 'pending'
        elif payment_status == 'online':
            payment_status = 'paid'
        else:
            payment_status = 'pending' 
            
        if not user_id or not product_ids or not total_amount:
            return Response({'error': 'Incomplete data provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        order = Order.objects.create(
            user=user,
            
            total_amount=total_amount,
            payment_status=payment_status,
            order_status=order_status)
        order.save()
       
        for product_id in product_ids:
            try:
                product = Product.objects.get(pk=product_id)
                order_item = OrderItem.objects.create(order=order, product=product, quantity=1)
                order_item.save()
            except Product.DoesNotExist:
                return Response({'error': f'Product with ID {product_id} not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"message":"Order successfully created"}, status=status.HTTP_201_CREATED)
    
class OrderStatusUpdate(APIView):
    # permission_classes = [IsAuthenticated,IsSuperAdmin]
    def put(self, request, order_id):
        try: 
            order = Order.objects.get(id=order_id)

            payment_status = request.data.get('payment_status', order.payment_status)  # Use the existing payment_status if not provided
            if payment_status == 'cod':
                payment_status = 'pending'
            elif payment_status == 'online':
                payment_status = 'paid'
            else:
                payment_status = 'pending'

            order_status = request.data.get('order_status', order.order_status)  # Use the existing order_status if not provided

            order.payment_status = payment_status
            order.order_status = order_status
            order.save()

            serializer = OrderStatusUpdateSerializer(order)
            return Response({"message": "Order updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        
#GET ALL ORDER API
class OrderItemView(APIView):
    def get(self, request):
        order_items = OrderItem.objects.all()
        order_item_data = []
        for order_item in order_items:
            order_item_data.append({
                'order_id': order_item.order.id,
                'product_id': order_item.product.id,
                'quantity': order_item.quantity,
            })
        return Response(order_item_data)

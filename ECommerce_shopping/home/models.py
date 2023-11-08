from django.db import models

from django.contrib.auth.models import AbstractUser
import datetime
PAYMENT_STATUS = (
    ('paid', 'Paid'),
    ('cod', 'COD'),
    ('online', 'Online'),
    ('pending', 'Pending') 
    
)
ORDER_STATUS_CHOICES = (
    ('delivered', 'Delivered'),
    ('pending', 'Pending')
)
class CustomUser(AbstractUser):
    otp = models.CharField(max_length=6,blank=True,null=True)
    is_user = models.BooleanField(default=False)
    is_cart = models.BooleanField(default=False)


    def __str__(self):
        if self.username:
            return self.username
        elif self.email:
            return self.email
        else:
            return f"User {self.id}"
class Otp(models.Model):
    mobile_number = models.CharField(max_length=12)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
    def __str__(self):
        return str(self.otp)
    
# Category model to categorize products
class Category(models.Model):
    category_name = models.CharField(max_length=100)
    

    def __str__(self):
        return self.category_name

# Product model with a foreign key to Category
class Product(models.Model):
    product_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)

    def __str__(self):
        return self.product_name
    
class ProductPicture(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_picture')
    product_picture = models.FileField(upload_to='product/docs')
    def __str__(self):
        return f"product_Picture {self.id}"


# Profile model to extend the User model (you can use the built-in User model)
class UserDetail(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    address = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=20)
    pin_code = models.CharField(max_length=6)
    profile = models.FileField(upload_to='register/docs',null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)

    def __str__(self):
        return self.user.username


class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)    
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
    
    def __str__(self):
        return self.quantity


# Order model to store order information
class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)   
    payment_status = models.CharField(choices=PAYMENT_STATUS, max_length=100)
    order_status = models.CharField(choices=ORDER_STATUS_CHOICES, max_length=100, default='pending')
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
    
    def __str__(self):
       
        return f"Order {self.id} - {self.order_date.strftime('%Y-%m-%d %H:%M:%S')}"


# Intermediate model for the Order-Product relationship with quantity
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def total_price(self):
        return self.quantity * self.product.price

from django.urls import path,include
from rest_framework import routers
from .user_api import *
from .super_admin import *

router = routers.DefaultRouter()
urlpatterns = [
    path('', include(router.urls)),
    #SUPERUSER APIS
    path('user-details/', UserDetailAPI.as_view(), name='user-details'),
    path('user-details-update/<int:userdetails_id>/', UserDetailUpdateAPI.as_view(), name='user-details-update'),
    path('user-genrate-otp/', GenrateOtpMobile.as_view(), name='user-register'),
    path('verify-otp/', VerifyOTP.as_view(), name='verify-otp'),
    path('product_create/', ProductCreateAPI.as_view(), name='product_create'),
    path('product_update/<int:product_id>/', ProductUpdateRetriveDeleteAPI.as_view(), name='product_update'),
    
    #ORDER
    path('order_create/', OrderCreateAPI.as_view(), name='order_create'),
    path('order_status_update/<int:order_id>/', OrderStatusUpdate.as_view(), name='order_status_update'),
    path('orderitem_get/', OrderItemView.as_view(), name='order_create'),
    
    #CART
    path('cart_item_create/', CartItemCreate.as_view(), name='cart_create'),
    path('cart_item_update/<int:cart_item_id>/', CartItemUpdateRetrive.as_view(), name='cart_update'),
    
    #CATEGORY
    path('category/', CategoryListCreate.as_view(), name='category-list-create'),
    path('category-delete/<int:category_id>/', CategoryRetrieveUpdateDestroyView.as_view(), name='category-list-create'),
    
    #USER LOGIN
    path('user-login/', UserLogin.as_view(), name='user-register'),
    path('otp-login-verify/', OTPLoginVerify.as_view(), name='user-register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
]
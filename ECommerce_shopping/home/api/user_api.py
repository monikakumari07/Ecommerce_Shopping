from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from ..models import *
from .serializer import *
from .custom_authentication import OTPAuthenticationBackend
import random
# from .permission import *
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token

class GenrateOtpMobile(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        mobile_number = request.data.get('mobile_number')       
        try:                
            otp = str(random.randint(100000,999999))
            Otp.objects.create(otp=otp, mobile_number=mobile_number)
            return Response({"otp": otp}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"message": "User is not active"}, status=status.HTTP_400_BAD_REQUEST)
        
class VerifyOTP(APIView):
    def post(self, request):
       
        otp = request.data.get('otp')        
        try:
            otp_obj = Otp.objects.get( otp=otp)
            print(otp_obj)
            otp_obj.delete()
        except Otp.DoesNotExist:
            return Response({"error": "Invalid OTP or mobile number"}, status=status.HTTP_400_BAD_REQUEST)

       
        return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)


class UserDetailAPI(APIView):
    def get(self, request):
        userdetail_get_all = UserDetail.objects.all()
        serializer = UserDetailSerializer(userdetail_get_all, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self,request):
        name=request.data['name']
        mobile_number = request.data['mobile_number']
        if not mobile_number or not mobile_number.isdigit():
            return Response({"message":"mobile number should be Numerical"}, status=status.HTTP_400_BAD_REQUEST)
        if len(mobile_number)!=10:
            return Response({"message":"mobile number should be 10 digit"}, status=status.HTTP_400_BAD_REQUEST)         
        email = request.data['email']
        address = request.data['address']
        pin_code = request.data['pin_code']
        profile = request.FILES['profile']  
        if CustomUser.objects.filter(username=mobile_number).exists():
            return Response({"message": "Already Register. Please use a different mobile number."}, status=status.HTTP_400_BAD_REQUEST)
        user = CustomUser.objects.create_user(
            username=mobile_number, email=email)
        register = UserDetail.objects.create(
            user=user,
            name=name,
            mobile_number=mobile_number,
            address =address,
            pin_code=pin_code,
            profile=profile
        )  
        user.is_user = True      
        user.save()
        
        serializer = UserDetailSerializer(register)
        response = {
                "result": serializer.data,
                "status": 1
            }
        
        return Response(response)
    
#USERDETAILS UPDATE
class UserDetailUpdateAPI(APIView):
    def put(self, request, userdetails_id):
        try:
            user_details = UserDetail.objects.get(id=userdetails_id)
        except UserDetail.DoesNotExist:
            return Response({"message": "Id does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        user_details.name = request.data.get('name', user_details.name)
        exist_mobile_number = CustomUser.objects.filter(username=request.data.get('mobile_number')).exclude(id=user_details.user.id)
        if exist_mobile_number:
            return Response({"message": "Already Registered. Enter Another number"}, status=status.HTTP_400_BAD_REQUEST)
        user_details.mobile_number = request.data.get('mobile_number', user_details.mobile_number)
        
        user_details.address = request.data.get('address', user_details.address)
        user_details.pin_code = request.data.get('pin_code', user_details.pin_code)
        user_details.profile = request.data.get('profile', user_details.profile)
        user_details.save()
        
        user = user_details.user
        if user:
            user.username = request.data.get("mobile_number")
            user.save()
        
        serializer = UserDetailSerializer(user_details)
        return Response({"message": "Successfully updated User details.", "data": serializer.data}, status=status.HTTP_200_OK)

#DELETE USERDETAILS
    def delete(self,request,userdetails_id):
        try:
            obj_userdetails = UserDetail.objects.get(id=userdetails_id)
        except UserDetail.DoesNotExist:
            return Response({"message":"Id does not exist"},status=status.HTTP_400_BAD_REQUEST)
        obj_userdetails.delete()
        return Response({"message":"ID Delete Sucessfully"},status=status.HTTP_200_OK)

    def get(self,request,userdetails_id):
        if userdetails_id:
            userdeatil_get_id = UserDetail.objects.get(id=userdetails_id)
            serializer = UserDetailSerializer(userdeatil_get_id)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        
      

#USER LOGIN
class UserLogin(APIView):
    def post(self, request):
        mobile_number = request.data.get('mobile_number')
        print(mobile_number)
       
        try:
            user = CustomUser.objects.get(username=mobile_number)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found or not registered"}, status=status.HTTP_404_NOT_FOUND)
        print(user)
        new_otp = str(random.randint(100000, 999999))
        user.otp = new_otp
        user.save()
        
        return Response({"otp": new_otp}, status=status.HTTP_200_OK)


class OTPLoginVerify(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        otp = request.data.get('otp')
        
        
        user_obj = CustomUser.objects.filter(otp=otp).exists()
        if user_obj:
            user = OTPAuthenticationBackend.authenticate(self,request,otp=otp)
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "message" : 'Success',
                "token": str(token.key),
            })
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
#LOGOUT

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):  
        user = request.user
        try:            
            token = Token.objects.get(user=user)  # token associated with the user and delete it
            token.delete()            
            return Response({"detail": "Successfully logged out."})
        except Token.DoesNotExist:
            return Response({"detail": "Invalid token."}, status=400)
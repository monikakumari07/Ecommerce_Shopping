from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
CustomUser = get_user_model()
class OTPAuthenticationBackend(BaseBackend):
    def authenticate(self, request, otp=None, **kwargs):
        # Check if OTP is provided
        if otp is None:
            return None
        # Retrieve the user based on the OTP
        try:
            user = CustomUser.objects.get(otp=otp)
        except CustomUser.DoesNotExist:
            return None
        # Clear the OTP after successful authentication
        user.otp = None
        user.save()
        if user is not None:
            user.backend = 'home.api.custom_authentication.OTPAuthenticationBackend'
            return user
    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None





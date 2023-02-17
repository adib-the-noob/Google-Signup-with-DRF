from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token

from .serializers import SignUpSerializer, LoginSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Verify the Google ID token
        token = serializer.validated_data['token']
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request())
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
        except ValueError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        # Create or retrieve the user account
        email = idinfo['email']
        full_name = idinfo['name']
        username = idinfo['given_name']
        print(email)
        print(full_name)
        print(username)
        with open('email.txt', 'w') as f:
            f.write(email)
            f.write('----')
            f.write(full_name)
            f.write('----')       
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create(email=email, username=username)
            user.set_unusable_password()
            user.save() 

        # Generate a JWT access token
        access_token = AccessToken.for_user(user)
        return Response({'access_token': str(access_token)}, status=status.HTTP_200_OK)

class TestView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({'message': 'Hello, world!'}, status=status.HTTP_200_OK)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Verify the Google ID token
        token = serializer.validated_data['token']
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request())
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
        except ValueError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user account exists
        email = idinfo['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User account does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Generate a JWT access token
        access_token = AccessToken.for_user(user)
        return Response({'access_token': str(access_token)}, status=status.HTTP_200_OK)
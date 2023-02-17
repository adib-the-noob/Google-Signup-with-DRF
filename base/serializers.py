from rest_framework import serializers
from django.contrib.auth import get_user_model
from google.oauth2 import id_token
from google.auth.transport import requests

User = get_user_model()

class SignUpSerializer(serializers.Serializer):
    token = serializers.CharField()

    def create(self, validated_data):
        token = validated_data['token']

        # Verify the Google ID token
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request())
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
        except ValueError:
            raise serializers.ValidationError('Invalid token')

        # Create the user account
        email = idinfo['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(email=email)

        return user

class LoginSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, data):
        token = data['token']

        # Verify the Google ID token
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request())
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
        except ValueError:
            raise serializers.ValidationError('Invalid token')

        # Retrieve the user account
        email = idinfo['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('User account does not exist')

        data['user'] = user
        return data

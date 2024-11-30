from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # Include necessary fields


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nested serializer to include User details

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'role']  # Include fields you want to serialize
from rest_framework import serializers
from .models import Document
from django.contrib.auth.models import User

class DocumentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Represent user as a string (username)

    class Meta:
        model = Document
        fields = ['id', 'user', 'file', 'uploaded_at']  # Include necessary fields
        read_only_fields = ['id', 'user', 'uploaded_at']  # These fields will not be writable

    def create(self, validated_data):
        # Ensure that only users with 'operational' role can upload documents
        user = self.context['request'].user
        user_profile = user.userprofile  # Access the user's profile
        if user_profile.role != 'operational':
            raise serializers.ValidationError("Only operational users can upload documents.")

        # Save the document with the current user
        document = Document.objects.create(user=user, **validated_data)
        return document

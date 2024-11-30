# models.py (in your app)

from django.db import models
from django.contrib.auth.models import User
from users.models import UserProfile  # Import the UserProfile model
from django.utils.timezone import now, timedelta


class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link the document to a user
    file = models.FileField(upload_to='documents/')  # Store documents in the 'documents' directory
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Record the time of upload

    def __str__(self):
        return f"Document uploaded by {self.user.username} on {self.uploaded_at}"

    def save(self, *args, **kwargs):
        # Ensure that only users with 'operational' role can upload documents
        user_profile = self.user.userprofile  # Access the user's profile
        if user_profile.role != 'operational':
            raise PermissionError("Only operational users can upload documents.")
        super().save(*args, **kwargs)  # Proceed with saving the document





class FileDownloadToken(models.Model):
    token = models.CharField(max_length=64, unique=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return now() <= self.expires_at

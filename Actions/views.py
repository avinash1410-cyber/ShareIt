from django.shortcuts import render, redirect
from .models import Document
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse,FileResponse
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view
from .serializers import DocumentSerializer
from django.shortcuts import get_object_or_404


import hashlib
import secrets
from django.utils.timezone import now, timedelta










# Utility to get JWT tokens from session
def get_jwt_from_session(request):
    access_token = request.session.get('access_token')
    refresh_token = request.session.get('refresh_token')
    return access_token, refresh_token




@api_view(['POST'])
@login_required  # Ensure the user is logged in
def upload_file(request):
    # Check if the user has the 'operational' role
    if request.user.userprofile.role != 'operational':
        return HttpResponseForbidden("You are not authorized to access this page.")

    if request.method == 'POST':
        # Check if a file is included in the request
        if 'file' not in request.FILES:
            return JsonResponse({"error": "No file provided"}, status=400)

        file = request.FILES['file']
        valid_extensions = ['pptx', 'docx', 'xlsx']
        if not file.name.split('.')[-1].lower() in valid_extensions:
            return JsonResponse({"error": f"Invalid file type. Allowed types: {', '.join(valid_extensions)}"}, status=400)

        try:
            # Save the file to the database
            document = Document(user=request.user, file=file)
            document.save()
            return JsonResponse({"message": "File uploaded successfully", "document_id": document.id}, status=201)

        except PermissionDenied as e:
            return JsonResponse({"error": str(e)}, status=403)
        except Exception as e:
            return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)




@api_view(['GET'])
@login_required
def available_files(request):
    files = Document.objects.all()  # Operational users can see all files
    serializer = DocumentSerializer(files, many=True)
    return Response(serializer.data)
    






@api_view(['POST'])
@login_required
def generate_download_link(request, file_id):
    try:
        document = get_object_or_404(Document, id=file_id)

        # Ensure only the owner can generate a link (optional)
        if request.user != document.user:
            return Response({"error": "Unauthorized to generate a download link for this file."}, status=403)

        # Generate a secure token
        token = hashlib.sha256(secrets.token_bytes(32)).hexdigest()

        # Save the token with a 10-minute expiration
        FileDownloadToken.objects.create(
            token=token,
            document=document,
            user=request.user,
            expires_at=now() + timedelta(minutes=10)
        )

        # Generate the encrypted URL
        download_url = f"{request.build_absolute_uri('/download-secure/')}{token}/"

        return Response({"download_url": download_url}, status=200)

    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=500)




from django.http import FileResponse

@api_view(['GET'])
def download_secure(request, token):
    try:
        # Find the token and validate
        token_entry = get_object_or_404(FileDownloadToken, token=token)

        # Check if the token is expired
        if not token_entry.is_valid():
            return Response({"error": "The link has expired."}, status=403)

        # Check if the user is authorized (optional)
        if request.user != token_entry.user:
            return Response({"error": "You are not authorized to download this file."}, status=403)

        # Serve the file
        document = token_entry.document
        response = FileResponse(
            document.file.open('rb'),
            as_attachment=True,
            filename=document.file.name.split('/')[-1]
        )
        return response

    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=500)



@api_view(['GET'])
@login_required
def download_file(request, file_id):
    if request.user.userprofile.role != 'client':
        return HttpResponseForbidden("You can not Download file as u are not an client.")
    try:
        document = get_object_or_404(Document, id=file_id)
        response = FileResponse(document.file.open('rb'), as_attachment=True, filename=document.file.name.split('/')[-1])
        return response
    except Exception as e:
        return HttpResponseForbidden(f"An error occurred: {str(e)}")


@api_view(['GET'])
@login_required
def protected_view(request):
    # Access the access token from the session
    access_token = request.session.get('access_token')
    print(request.user)

    if not access_token:
        return Response({"message": "Unauthorized - Token not found"}, status=401)

    # Authenticate the user with the token
    jwt_auth = JWTAuthentication()
    try:
        # This will use the access_token in request headers
        user, _ = jwt_auth.authenticate(request)
        return Response({"message": f"Welcome Mr {user.username}"})
    except Exception as e:
        return Response({"message": f"Authentication failed: {str(e)}"}, status=401)

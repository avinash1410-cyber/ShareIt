from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import UserProfile
from django.core.exceptions import ObjectDoesNotExist


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse
from users.models import UserProfile
from django.conf import settings

# Generate a unique token for email verification
from django.contrib.auth.tokens import default_token_generator as token_generator








from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator as token_generator

@api_view(['GET'])
def verify_email(request, uidb64, token):
    try:
        # Decode user ID
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)

        # Check the token
        if token_generator.check_token(user, token):
            user.is_active = True  # Activate the user
            user.save()
            return Response({"message": "Email verified successfully. You can now log in."})
        else:
            return Response({"message": "Invalid or expired token."}, status=400)

    except Exception as e:
        return Response({"message": f"An error occurred: {str(e)}"}, status=400)








# Function to generate tokens
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
def login_page(request):
    if request.method == "POST":
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"message": "Username and password are required."}, status=400)

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # If user is valid, generate JWT tokens
            tokens = get_tokens_for_user(user)

            # Store tokens in session
            request.session['access_token'] = tokens['access']
            request.session['refresh_token'] = tokens['refresh']

            return Response({
                "message": "Login successful",
                "tokens": tokens,
                "username": user.username,
                "role": user.userprofile.role if hasattr(user, 'userprofile') else 'Unknown',
                "email": user.email
            })
        else:
            return Response({"message": "Invalid credentials"}, status=401)

    return Response({"message": "Please provide valid credentials."}, status=400)


@api_view(['POST'])
def register_page(request):
    if request.method == "POST":
        # Extract data from the request
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        role = request.data.get('role')  # Either 'client' or 'operational'

        if not username or not password or not email:
            return Response({"message": "Username, password, and email are required."}, status=400)

        # Validate the role
        if role not in ['client', 'operational']:
            return Response({"message": "Invalid role. Role must be 'client' or 'operational'."}, status=400)

        try:
            # Create the user and associated UserProfile
            user = get_user_model().objects.create_user(username=username, password=password, email=email)
            UserProfile.objects.create(user=user, role=role)
            user.is_active = False  # Deactivate the user until email is verified
            user.save()

            # Generate an encrypted URL for email verification
            uid = urlsafe_base64_encode(force_bytes(user.pk))  # Encode the user ID
            token = token_generator.make_token(user)  # Create a unique token
            verify_url = request.build_absolute_uri(
                reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
            )

            # Send verification email
            send_mail(
                subject="Verify Your Email",
                message=f"Hello {username},\n\nPlease verify your email by clicking the link below:\n{verify_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )

        except Exception as e:
            # Handle duplicate username error
            if 'auth_user.username' in str(e):
                return Response({"message": "Username already exists. Please choose a different username."}, status=400)
            # For any other error
            return Response({"message": f"An unexpected error occurred: {str(e)}"}, status=500)

        return Response({
            "message": f"Registration successful as a {role} user. Verification email sent to {email}.",
            "verify_url": verify_url,  # Include encrypted URL in response (for debugging or testing)
        })

    # Default response for GET request
    return Response({
        "username": "",
        "password": "",
        "email": "",
        "role": "client/operational"
    })







@api_view(['POST'])
def refresh_token_view(request):
    refresh_token = request.session.get('refresh_token')

    if not refresh_token:
        return Response({"message": "No refresh token found"}, status=400)

    try:
        refresh = RefreshToken(refresh_token)
        new_access_token = str(refresh.access_token)

        # Store the new access token in session
        request.session['access_token'] = new_access_token

        return Response({"message": "Access token refreshed", "access_token": new_access_token})
    except Exception as e:
        return Response({"message": f"Error refreshing token: {str(e)}"}, status=400)


@api_view(['POST'])
def logout_page(request):
    # Clear the session tokens
    request.session.flush()  # This will clear all session data, including JWT tokens
    return Response({"message": "Logout successful"})

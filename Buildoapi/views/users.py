from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from Buildoapi.models.user import RareUser
from .rareusers import RareUserSerializer

# Define UserSerializer separately
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email', 'password')  
        extra_kwargs = {'password': {'write_only': True}}

class UserViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'], url_path='register')
    def register_account(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = User.objects.create_user(
                username=user_serializer.validated_data['username'],
                first_name=user_serializer.validated_data.get('first_name', ''),
                last_name=user_serializer.validated_data.get('last_name', ''),
                email=user_serializer.validated_data.get('email', ''),
                password=user_serializer.validated_data['password']
            )
            
            rare_user = RareUser.objects.create(
                bio=request.data.get('bio', ''),
                profile_image_url=request.data.get('profile_image_url', ''),
                state_name=request.data.get('state_name', ''),
                county_name=request.data.get('county_name', ''),
                is_contractor=request.data.get('is_contractor', False),
                qualifications=request.data.get('qualifications', ''),
                user=user
            )
            token, created = Token.objects.get_or_create(user=user)

            data = {
                'valid': True,
                'token': token.key,
                'staff': token.user.is_staff,
                'id': token.user.id,
                'first_name': token.user.first_name,
                'last_name': token.user.last_name,
                'username': token.user.username,
                'email': token.user.email,
                'bio': rare_user.bio,
                'profile_image_url': rare_user.profile_image_url,
                'state_name': rare_user.state_name,
                'county_name': rare_user.county_name,
                'is_contractor': rare_user.is_contractor,
                'qualifications':rare_user.qualifications
            }

            rare_user_serializer = RareUserSerializer(data=request.data, context={"request": request})
            if rare_user_serializer.is_valid():
                return Response(data, status=status.HTTP_201_CREATED)

            user.delete()
            return Response({'error': 'Failed to serialize RareUser'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='login')
    def login_user(self, request):
        username = request.data['username']
        password = request.data['password']

        authenticated_user = authenticate(username=username, password=password)

        if authenticated_user is not None:
            token = Token.objects.get(user=authenticated_user)

        # Access the associated RareUser instance for the authenticated user
            try:
                rare_user = RareUser.objects.get(user=authenticated_user)
                rare_user_data = {
                    'bio': rare_user.bio,
                    'profile_image_url': rare_user.profile_image_url,
                    'state_name': rare_user.state_name,
                    'county_name': rare_user.county_name,
                    'is_contractor': rare_user.is_contractor,
                }
            except RareUser.DoesNotExist:
                rare_user_data = {}

            data = {
                'valid': True,
                'token': token.key,
                'staff': token.user.is_staff,
                'id': token.user.id,
                'first_name': token.user.first_name,
                'last_name': token.user.last_name,
                'username': token.user.username,
                'email': token.user.email,
                'rare_user': rare_user_data,
            }

            return Response(data)
        else:
            data = {'valid': False, 'error': 'Invalid username or password'}
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
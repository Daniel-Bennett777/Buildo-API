from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from Buildoapi.models.user import RareUser
from .rareusers import RareUserSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email', 'password')  # add other fields as needed
        extra_kwargs = {'password': {'write_only': True}}

class UserViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'], url_path='register')
    def register_account(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            # Create the User instance
            user = User.objects.create_user(
                username=user_serializer.validated_data['username'],
                first_name=user_serializer.validated_data.get('first_name', ''),
                last_name=user_serializer.validated_data.get('last_name', ''),
                email=user_serializer.validated_data.get('email', ''),
                password=user_serializer.validated_data['password']
            )
            
            # Create Token for the User
            token, created = Token.objects.get_or_create(user=user)

            data = {
                'valid': True,
                'token': token.key,
                'staff': token.user.is_staff,
                'id': token.user.id
            }

            # Create the RareUser instance
            rare_user =  RareUser.objects.create(
                bio = request.data.get('bio', ''),
                profile_image_url = request.data.get('profile_image_url', ''),
                state_name = request.data.get('state_name', ''),
                county_name = request.data.get('county_name', ''),
                is_contractor = request.data.get('is_contractor', False),
                user = user
            )
            
            
            rare_user_data = RareUserSerializer(rare_user, context={"request": request}).data

            if rare_user_data:  # Check if serialization is successful
                return Response(data, status=status.HTTP_201_CREATED)



            # If RareUser creation fails, delete the user and return an error response
            
            user.delete()
            return Response({'error': 'Failed to serialize RareUser'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    @action(detail=False, methods=['post'], url_path='login')
    def login_user(self, request):
        '''Handles the authentication of a user

        Method arguments:
        request -- The full HTTP request object
        '''
        username = request.data['username']
        password = request.data['password']

        # Use the built-in authenticate method to verify
        # authenticate returns the user object or None if no user is found
        authenticated_user = authenticate(username=username, password=password)

        # If authentication was successful, respond with their token
        if authenticated_user is not None:
            token = Token.objects.get(user=authenticated_user)

            data = {
                'valid': True,
                'token': token.key,
                'staff': token.user.is_staff,
                'id': token.user.id
            }
            return Response(data)
        else:
            # Bad login details were provided. So we can't log the user in.
            data = { 'valid': False }
            return Response(data)
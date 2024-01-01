from rest_framework import viewsets
from rest_framework import serializers
from Buildoapi.models.user import RareUser


class RareUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    class Meta:
        model = RareUser
        fields = ('id', 'bio', 'profile_image_url', 'created_on', 'active', 'user_id', 'state_name', 'county_name', 'is_contractor', "qualifications",'username', 'last_name','first_name')
        
class RareUserViewSet(viewsets.ViewSet):
    pass     
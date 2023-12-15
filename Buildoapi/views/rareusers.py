from rest_framework import viewsets
from rest_framework import serializers
from Buildoapi.models.user import RareUser


class RareUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RareUser
        fields = ('id', 'bio', 'profile_image_url', 'created_on', 'active', 'user_id', 'state_name', 'county_name', 'is_contractor', "qualifications")
        
class RareUserViewSet(viewsets.ViewSet):
    pass     
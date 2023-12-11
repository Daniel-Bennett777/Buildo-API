from rest_framework import viewsets, serializers, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from Buildoapi.models.review import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__' 
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated] 
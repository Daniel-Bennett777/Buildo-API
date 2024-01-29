from rest_framework import viewsets
from rest_framework.response import Response
from Buildoapi.models import Connection, RareUser, RequestStatus, ConnectionRequest
from Buildoapi.views import ConnectionSerializer
from django.db.models import Q

class ConnectionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConnectionSerializer

    def get_queryset(self):
        user = RareUser.objects.get(user=self.request.user.id)


        return Connection.objects.filter(
            (Q(user1=user, user2_cellphone__isnull=False, user2_cellphone__gt='')) |
            (Q(user2=user, user2_cellphone__isnull=False, user2_cellphone__gt=''))
        ).distinct()


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
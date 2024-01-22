from rest_framework import viewsets, status
from rest_framework import serializers
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from Buildoapi.models import ConnectionRequest, Connection , RareUser, RequestStatus


class RequestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestStatus
        fields = '__all__'

class ConnectionRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConnectionRequest
        fields = '__all__'

class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = '__all__'

class ConnectionRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ConnectionRequestSerializer

    def create(self, request, *args, **kwargs):
        sender = RareUser.objects.get(user=request.user.id)
        receiver_id = request.data.get('receiver')

        # Get the receiver (contractor) and customer information
        receiver = get_object_or_404(RareUser, id=receiver_id, is_contractor=True)
        customer = RareUser.objects.get(user=request.user.id)

        # Ensure the sender is not trying to send a request to themselves
        if sender == receiver_id:
            return Response({"message": "Cannot send a request to yourself."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a request already exists
        existing_request = ConnectionRequest.objects.filter(sender_id=sender, receiver_id=receiver_id).exists()

        if existing_request:
            return Response({"message": "Connection request already sent."}, status=status.HTTP_400_BAD_REQUEST)

        #try to get the request status instance 
        request_status_id = request.data.get("RequestStatus")
        try:
            request_status = RequestStatus.objects.get(id=1)
            print(request_status.status)
        except RequestStatus.DoesNotExist:
            print("RequestStatus with ID 1 does not exist.")


        # Create the connection request with customer information in the message
        message = f"{customer.user.first_name} {customer.user.last_name} wants to connect with you."
        request_data = {'sender': sender.id, 
                        'receiver': receiver_id, 
                        'message': message,
                        'status': request_status.id}
        serializer = ConnectionRequestSerializer(data=request_data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(sender=sender)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
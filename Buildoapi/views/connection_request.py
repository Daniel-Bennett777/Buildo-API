from rest_framework import viewsets, status
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from Buildoapi.models import ConnectionRequest, RareUser, RequestStatus, Connection

class ConnectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Connection
        fields = '__all__'

class RequestStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = RequestStatus
        fields = '__all__'

class ConnectionRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConnectionRequest
        fields = '__all__'

class ConnectionRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ConnectionRequestSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = RareUser.objects.get(user=self.request.user.id)
        return ConnectionRequest.objects.filter(receiver=user, status=1)

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

        try:
            request_status = RequestStatus.objects.get(id=1)
            print(request_status.status)
        except RequestStatus.DoesNotExist:
            print("RequestStatus with ID 1 does not exist.")


        # Create the connection request with customer information in the message
        message = f"{customer.user.first_name} {customer.user.last_name} wants to connect with you."
        request_data = {'sender': sender.id, 
                        'receiver': receiver.id, 
                        'message': message,
                        'status': request_status.id}
        serializer = ConnectionRequestSerializer(data=request_data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(sender=sender)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        action = request.data.get('action')

        if action == 'accept':
            accepted_status = RequestStatus.objects.get(status='Accepted')
            instance.status = accepted_status
            # If the connection request is accepted, create a connection instance
            if instance.status == accepted_status:
                # Check if the contractor's phone number is provided
                if 'user2_cellphone' not in request.data:
                    return Response({'error': 'Contractor\'s phone number is required to accept the connection request'},
                                    status=status.HTTP_400_BAD_REQUEST)

                # Create a Connection instance using the information from the ConnectionRequest
                connection_data = {
                    'user1': instance.sender.pk,
                    'user2': instance.receiver.pk,
                    'user2_cellphone': request.data.get('user2_cellphone'),
                }
                
                connection_serializer = ConnectionSerializer(data=connection_data)

                if connection_serializer.is_valid():
                    connection_serializer.save()

                    # Save the status after creating the connection instance
                    instance.save()

                    return Response({'status': 'accepted and connection created'})

                return Response({'error': 'Error creating connection'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'reject':
            rejected_status = RequestStatus.objects.get(status='Rejected')
            instance.status = rejected_status

            # Create a Connection instance for rejected requests
            connection_data = {
                'user1': instance.sender.pk,
                'user2': instance.receiver.pk,
            }

            connection_serializer = ConnectionSerializer(data=connection_data, partial=True)

            if connection_serializer.is_valid():
                connection_serializer.save()

                # Save the status after creating the connection instance
                instance.save()

                return Response({'status': 'rejected and connection created'})

            return Response({'error': 'Error creating connection'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
# Import necessary modules and classes from Django and Django REST Framework
from django.contrib.auth.models import User
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from Buildoapi.models import Message, RareUser

# Define a serializer for extracting specific fields from the User model
class UserMessagesSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    # Define a method to concatenate first and last names into a full name
    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'

    class Meta:
        model = User
        fields = ['full_name', 'username']

# Define a serializer for RareUser model, including the UserMessagesSerializer
class RareUserMessageSerializer(serializers.ModelSerializer):
    user = UserMessagesSerializer(many=False)

    class Meta:
        model = RareUser
        fields = ['id', 'user', 'profile_image_url']

# Define a serializer for the Message model, including the RareUserMessageSerializer
class MessageSerializer(serializers.ModelSerializer):
    sender = RareUserMessageSerializer(many=False)
    receiver = RareUserMessageSerializer(many=False)

    class Meta:
        model = Message
        fields = '__all__'

# Define a ViewSet for handling messages
class MessagesView(ViewSet):
    
    # Define a method for handling GET requests to retrieve a list of messages
    def list(self, request):
        # Query sent and received messages for the current user
        sent_messages = Message.objects.filter(sender__user=request.user)
        received_messages = Message.objects.filter(receiver__user=request.user)
        
        # Combine sent and received messages into one queryset
        messages = sent_messages | received_messages
        
        # Sort the messages by date_sent if needed
        messages = messages.order_by('date_sent')
        
        # Serialize the messages and return the response
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    # Define a method for handling POST requests to create a new message
    def create(self, request):
        # Get the sender and receiver RareUser instances based on the request
        sender = RareUser.objects.get(user=request.auth.user)
        receiver = RareUser.objects.get(pk=request.data["receiver"])
        
        # Create a new Message instance and populate its fields
        m = Message()
        m.sender = sender
        m.receiver = receiver
        m.content = request.data.get('content')
        m.save()

        # Serialize the created message and return the response
        try:
            serializer = MessageSerializer(m, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

    # Define a method for handling DELETE requests to delete a message by ID
    def destroy(self, request, pk=None):
        try:
            # Attempt to get and delete the specified message
            message = Message.objects.get(pk=pk)
            message.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Message.DoesNotExist:
            # Return a 404 response if the specified message does not exist
            return Response(status=status.HTTP_404_NOT_FOUND)
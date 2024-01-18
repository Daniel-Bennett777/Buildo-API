from django.db import models
from .user import RareUser
from .connection import Connection

class Message(models.Model):
    sender = models.ForeignKey(RareUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(RareUser, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE, null=True, blank=True)
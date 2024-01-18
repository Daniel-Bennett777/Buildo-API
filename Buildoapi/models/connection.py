from django.db import models
from .user import RareUser

class Connection(models.Model):
    user1 = models.ForeignKey(RareUser, on_delete=models.CASCADE, related_name='user1_connections')
    user2 = models.ForeignKey(RareUser, on_delete=models.CASCADE, related_name='user2_connections')
    user2_cellphone = models.CharField(max_length=20)  # Cellphone number of user2
    date_connected = models.DateTimeField(auto_now_add=True)
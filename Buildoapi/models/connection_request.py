from django.db import models
from .user import RareUser
from .request_status import RequestStatus

class ConnectionRequest(models.Model):
    sender = models.ForeignKey(RareUser, on_delete=models.CASCADE, related_name='sent_connection_requests')
    receiver = models.ForeignKey(RareUser, on_delete=models.CASCADE, related_name='received_connection_requests')
    date_requested = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(RequestStatus, on_delete=models.CASCADE)
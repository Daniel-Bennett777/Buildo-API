from django.db import models

class RequestStatus(models.Model):
    status = models.CharField(max_length=20)  # Values like 'Pending', 'Accepted', 'Rejected'

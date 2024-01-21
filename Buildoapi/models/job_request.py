from django.db import models
from .user import RareUser
from .request_status import RequestStatus
from .work_order import WorkOrder

class JobRequest(models.Model):
    contractor = models.ForeignKey(RareUser, on_delete=models.CASCADE, related_name='contractor_requests')
    customer = models.ForeignKey(RareUser, on_delete=models.CASCADE, related_name='customer_requests')
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='job_requests')
    request_status = models.ForeignKey(RequestStatus, on_delete=models.CASCADE)
    date_requested = models.DateTimeField(auto_now_add=True)
    contractor_cellphone = models.CharField(max_length=20)  # Add the field for contractor's cellphone number
    accepted_by_customer = models.BooleanField(default=False)

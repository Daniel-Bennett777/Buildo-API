from django.db import models
from .user import RareUser
from .status import Status

class WorkOrder(models.Model):
    service_type = models.CharField(max_length=255)
    state_name = models.CharField(max_length=20)
    county_name = models.CharField(max_length=20)
    date_posted = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(RareUser, on_delete=models.CASCADE, related_name='customer_order')
    contractor = models.ForeignKey(RareUser, on_delete=models.SET_NULL, null=True,blank=True, related_name='contractor_order')
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    description = models.TextField()
    profile_image = models.ImageField(upload_to='work_order_images/', null=True, blank=True)

    def set_in_progress_status(self):
        in_progress_status = Status.objects.get(status='in-progress')
        self.status = in_progress_status
        self.save()
    def __str__(self):
        return f"WorkOrder {self.pk}: {self.service_type} - {self.state_name} - {self.county_name} - {self.date_posted}"
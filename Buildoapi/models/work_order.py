from django.db import models
from .users import RareUser
from .status import Status

class WorkOrder(models.Model):
    service_type = models.CharField(max_length=255)
    state_name = models.CharField(max_length=20)
    county_name = models.CharField(max_length=20)
    date_posted = models.DateTimeField()
    customer = models.ForeignKey(RareUser, on_delete=models.CASCADE, related_name='work_orders_posted')
    contractor = models.ForeignKey(RareUser, on_delete=models.SET_NULL, null=True, related_name='work_orders_accepted')
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    description = models.TextField()
    profile_image_url = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=155)

    def __str__(self):
        return f"WorkOrder {self.pk}: {self.service_type} - {self.state_name} - {self.county_name} - {self.date_posted}"
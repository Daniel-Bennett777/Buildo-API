from django.db import models
from .users import RareUser
from .rating import Rating

class Review(models.Model):
    customer = models.ForeignKey(RareUser, on_delete=models.CASCADE, related_name='work_orders_posted')
    contractor = models.ForeignKey(RareUser, on_delete=models.SET_NULL, null=True, related_name='work_orders_accepted')
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE)
    comment = models.TextField()
    date_posted = models.DateTimeField()
    profile_image_url = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=155)
    

    def __str__(self):
        return f"Review {self.pk}: {self.customer} - {self.contractor} - {self.rating} - {self.date_posted}"
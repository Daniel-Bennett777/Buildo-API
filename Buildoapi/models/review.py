from django.db import models
from .user import RareUser
from .rating import Rating

class Review(models.Model):
    customer = models.ForeignKey(RareUser, on_delete=models.CASCADE, related_name='customer_reviews')
    contractor = models.ForeignKey(RareUser, on_delete=models.SET_NULL, null=True, related_name='contractor_reviews')
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE)
    comment = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    profile_image_url = models.URLField(max_length=255) 
    

    def __str__(self):
        return f"Review {self.pk}: {self.customer} - {self.contractor} - {self.rating} - {self.date_posted}"
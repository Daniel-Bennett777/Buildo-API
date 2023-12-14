from django.db import models
from django.contrib.auth.models import User

class RareUser(models.Model):
    bio = models.CharField(max_length=155)
    profile_image_url = models.URLField(max_length=255) 
    created_on = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    state_name = models.CharField(max_length=20)
    county_name = models.CharField(max_length=20)
    is_contractor = models.BooleanField(default=False)
    qualifications = models.TextField(blank=True, null=True)

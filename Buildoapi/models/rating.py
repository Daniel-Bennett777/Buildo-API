from django.db import models

class Rating(models.Model):
    value = models.IntegerField()  # Numeric value from 1-5
    description = models.CharField(max_length=255, blank=True, null=True)  # Optional description

    def __str__(self):
        return f"Rating {self.pk}: {self.value}"
from django.db import models

class Status(models.Model):
    status = models.CharField(max_length=255)

    def __str__(self):
        return f"Status {self.pk}: {self.status}"
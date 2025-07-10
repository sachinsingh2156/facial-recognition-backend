from django.db import models

# Create your models here.

class User(models.Model):
    unique_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    face_embedding = models.TextField()  # Store as JSON or string

    def __str__(self):
        return self.name

from django.db import models

# Create your models here.
class Movies(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    year = models.IntegerField()
    genre = models.CharField(max_length=100)
    director = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

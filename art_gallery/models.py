from django.db import models

class Artwork(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=200)

    def __str__(self):
        return self.title
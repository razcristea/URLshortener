from django.db import models


# Create your models here.
class URLs(models.Model):
    long_url = models.URLField(max_length=256)
    short_url = models.CharField(max_length=8, unique=True)

    def __repr__(self):
        self.long_url = long_url
        self.short_url = short_url

from django.db import models


class Wine(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.FloatField(null=True, blank=True)
    wine_type = models.CharField(max_length=100, blank=True)
    abv = models.FloatField(null=True, blank=True)
    vintage = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    grape = models.CharField(max_length=100, blank=True)
    characteristics = models.TextField(blank=True)
    style = models.CharField(max_length=100, blank=True)
    capacity = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.title


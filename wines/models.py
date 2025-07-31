import os
import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.text import slugify
from django.conf import settings


def wine_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/wines/", filename)


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
    image = models.ImageField(null=True, blank=True, upload_to=wine_image_file_path)

    def __str__(self):
        return f"{self.title} ({self.vintage})" if self.vintage else self.title

    class Meta:
        ordering = ["title"]
        constraints = [
            UniqueConstraint(fields=["title", "vintage", "capacity"], name="unique_wine_entry")
        ]


class WineReview(models.Model):
    wine = models.ForeignKey(Wine, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Оцінка від 0 до 10",
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("wine", "user")  # only one review per wine per user
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} – {self.wine.title}: {self.rating}"

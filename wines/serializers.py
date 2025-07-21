from rest_framework import serializers

from wines.models import Wine


class WineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wine
        fields = (
            "id", "title", "description", "price", "wine_type", "abv",
            "vintage", "country", "region", "grape", "characteristics",
            "style", "capacity", "image"
        )


class WineListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wine
        fields = ("id", "title", "vintage", "price", "image")


class WineImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wine
        fields = ("id", "image")


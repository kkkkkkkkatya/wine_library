from rest_framework import serializers

from wines.models import Wine, WineReview


class WineReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    rating = serializers.IntegerField(min_value=0, max_value=10)

    class Meta:
        model = WineReview
        fields = ("id", "user", "rating", "comment", "created_at")


class WineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wine
        fields = (
            "id", "title", "description", "price", "wine_type", "abv",
            "vintage", "country", "region", "grape", "characteristics",
            "style", "capacity", "image"
        )


class WineListSerializer(WineSerializer):
    average_rating = serializers.FloatField(read_only=True, source="avg_rating")

    class Meta(WineSerializer.Meta):
        fields = ("id", "title", "vintage", "price", "image", "average_rating")


class WineDetailSerializer(WineSerializer):
    average_rating = serializers.FloatField(read_only=True, source="avg_rating")
    reviews = WineReviewSerializer(many=True, read_only=True)

    class Meta(WineSerializer.Meta):
        fields = WineSerializer.Meta.fields + ("average_rating", "reviews")


class WineImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wine
        fields = ("id", "image")

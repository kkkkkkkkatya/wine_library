from django.db.models import Avg
from rest_framework.response import Response
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

from wines.models import Wine, WineReview
from wines.permissions import IsAdminOrIfAuthenticatedReadOnly
from wines.serializers import WineSerializer, WineListSerializer, WineDetailSerializer, WineImageSerializer, WineReviewSerializer


class WineViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Wine.objects.all()
    serializer_class = WineSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        """Retrieve the wines with filters"""
        queryset = self.queryset.annotate(avg_rating=Avg("reviews__rating"))

        title = self.request.query_params.get("title")
        wine_type = self.request.query_params.get("wine_type")
        grape = self.request.query_params.get("grape")
        country = self.request.query_params.get("country")

        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")

        min_abv = self.request.query_params.get("min_abv")
        max_abv = self.request.query_params.get("max_abv")

        min_capacity = self.request.query_params.get("min_capacity")
        max_capacity = self.request.query_params.get("max_capacity")

        min_rating = self.request.query_params.get("min_rating")
        max_rating = self.request.query_params.get("max_rating")

        # Apply filters
        if title:
            queryset = queryset.filter(title__icontains=title)

        if wine_type:
            queryset = queryset.filter(wine_type__iexact=wine_type)

        if grape:
            queryset = queryset.filter(grape__icontains=grape)

        if country:
            queryset = queryset.filter(country__iexact=country)

        if min_price:
            queryset = queryset.filter(price__gte=float(min_price))
        if max_price:
            queryset = queryset.filter(price__lte=float(max_price))

        if min_abv:
            queryset = queryset.filter(abv__gte=float(min_abv))
        if max_abv:
            queryset = queryset.filter(abv__lte=float(max_abv))

        if min_capacity:
            queryset = queryset.filter(capacity__gte=float(min_capacity))
        if max_capacity:
            queryset = queryset.filter(capacity__lte=float(max_capacity))

        if min_rating:
            queryset = queryset.filter(avg_rating__gte=float(min_rating))
        if max_rating:
            queryset = queryset.filter(avg_rating__lte=float(max_rating))

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return WineListSerializer

        if self.action == "retrieve" or self.action == "save" or self.action == "unsave":
            return WineDetailSerializer

        if self.action == "upload_image":
            return WineImageSerializer

        if self.action == "add_review":
            return WineReviewSerializer

        return WineSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific wine"""
        wine = self.get_object()
        serializer = self.get_serializer(wine, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["POST"],
        detail=True,
        url_path="add-review",
        permission_classes=[IsAuthenticated],
    )
    def add_review(self, request, pk=None):
        """Create a review for a specific wine"""
        wine = self.get_object()

        if WineReview.objects.filter(wine=wine, user=request.user).exists():
            return Response(
                {"detail": "You have already reviewed this wine."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = WineReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, wine=wine)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def save(self, request, pk=None):
        """Add wine to user's saved list"""
        wine = self.get_object()
        user = request.user
        user.saved_wines.add(wine)
        return Response({"status": "Wine added to saved"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def unsave(self, request, pk=None):
        """Remove wine from user's saved list"""
        wine = self.get_object()
        user = request.user
        user.saved_wines.remove(wine)
        return Response({"status": "Wine removed from saved"}, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by wine title (ex. ?title=Laurent-Perrier)",
            ),
            OpenApiParameter(
                name="wine_type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by wine type (e.g., red, white, sparkling)",
            ),
            OpenApiParameter(
                name="grape",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by grape variety (e.g., cabernet)",
            ),
            OpenApiParameter(
                name="country",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by country of origin (e.g., France)",
            ),
            OpenApiParameter(
                name="min_price",
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
                description="Minimum price (e.g., ?min_price=10.0)",
            ),
            OpenApiParameter(
                name="max_price",
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
                description="Maximum price (e.g., ?max_price=50.0)",
            ),
            OpenApiParameter(
                name="min_abv",
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
                description="Minimum ABV (e.g., ?min_abv=11.5)",
            ),
            OpenApiParameter(
                name="max_abv",
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
                description="Maximum ABV (e.g., ?max_abv=14.0)",
            ),
            OpenApiParameter(
                name="min_capacity",
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
                description="Minimum capacity in ml (e.g., ?min_capacity=500)",
            ),
            OpenApiParameter(
                name="max_capacity",
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
                description="Maximum capacity in ml (e.g., ?max_capacity=1000)",
            ),
            OpenApiParameter(
                name="min_rating",
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
                description="Minimum average rating (e.g., ?min_rating=3.0)",
            ),
            OpenApiParameter(
                name="max_rating",
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
                description="Maximum average rating (e.g., ?max_rating=5.0)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

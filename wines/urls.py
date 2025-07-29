from django.urls import path, include
from rest_framework import routers

from wines.views import (
    WineViewSet,
)

router = routers.DefaultRouter()
router.register("wines", WineViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "wines"

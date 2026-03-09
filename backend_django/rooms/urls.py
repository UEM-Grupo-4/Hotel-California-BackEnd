from rest_framework.routers import DefaultRouter
from .views import RoomViewSet, RoomTypeViewSet, AmenityViewSet

router = DefaultRouter()

router.register(r'types', RoomTypeViewSet, basename='types')
router.register(r'amenities', AmenityViewSet, basename='amenities')
router.register(r'', RoomViewSet)

urlpatterns = router.urls

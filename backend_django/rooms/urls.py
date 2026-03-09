from rest_framework.routers import DefaultRouter
from .views import RoomViewSet, RoomTypeViewSet, AmenityViewSet

router = DefaultRouter()

router.register(r'', RoomViewSet)
router.register(r'types', RoomTypeViewSet, basename='type')
router.register(r'amenities', AmenityViewSet, basename='amenities')

urlpatterns = router.urls

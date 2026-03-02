from rest_framework.routers import DefaultRouter

from .views import HabitacionViewSet, TipoHabitacionViewSet

router = DefaultRouter()
router.register(r'habitaciones', HabitacionViewSet, basename='habitacion')
router.register(r'tipos-habitacion', TipoHabitacionViewSet, basename='tipo-habitacion')

urlpatterns = router.urls
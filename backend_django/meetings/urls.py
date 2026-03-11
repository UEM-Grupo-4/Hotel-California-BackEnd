from rest_framework.routers import DefaultRouter

from .views import SalaViewSet, HorarioSalaViewSet

router = DefaultRouter()
router.register(r'salas', SalaViewSet, basename='sala')
router.register(r'horarios', HorarioSalaViewSet, basename='horario')

urlpatterns = router.urls
from rest_framework.routers import DefaultRouter

from .views import ClienteViewSet, TelefonoViewSet

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'telefonos', TelefonoViewSet, basename='telefono')

urlpatterns = router.urls

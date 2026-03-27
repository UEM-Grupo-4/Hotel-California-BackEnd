from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ReservaViewSet,
    ReservaHabitacionViewSet,
    ReservaSalaViewSet,
    HabitacionesDisponiblesView,
    ReservaSearchView
)

router = DefaultRouter()
router.register(r"reservas", ReservaViewSet, basename="reservas")
router.register(r"reservas-habitaciones", ReservaHabitacionViewSet, basename="reservas-habitaciones")
router.register(r"reservas-salas", ReservaSalaViewSet, basename="reservas-salas")

urlpatterns = router.urls + [
    path("habitaciones/disponibles/", HabitacionesDisponiblesView.as_view(), name="habitaciones-disponibles"),
    path("reservas/search/", ReservaSearchView.as_view()),
]

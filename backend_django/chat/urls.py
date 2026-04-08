from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet, close_conversation

router = DefaultRouter()
router.register(r"conversations", ConversationViewSet)
router.register(r"messages", MessageViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("<int:pk>/close/", close_conversation),
]

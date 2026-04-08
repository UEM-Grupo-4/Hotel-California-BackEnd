from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from rest_framework.permissions import AllowAny

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().order_by("-created_at")
    permission_classes = [AllowAny]
    serializer_class = ConversationSerializer

    def perform_create(self, serializer):
        conversation = serializer.save()

        initial_message = self.request.data.get("initial_message")

        if initial_message:
            Message.objects.create(
                conversation=conversation,
                content=initial_message,
                sender="user",
            )

    @action(detail=False, methods=["get"])
    def by_email(self, request):
        email = request.query_params.get("email")

        if not email:
            return Response({"error": "email requerido"}, status=400)

        conversations = Conversation.objects.filter(user_email=email)

        serializer = self.get_serializer(conversations, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by("created_at")
    permission_classes = [AllowAny]
    serializer_class = MessageSerializer

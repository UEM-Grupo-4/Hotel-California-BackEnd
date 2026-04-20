from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from rest_framework.permissions import AllowAny
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@api_view(["PATCH"])
def close_conversation(request, pk):
    try:
        conversation = Conversation.objects.get(pk=pk)
        conversation.is_closed = True
        conversation.save()

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f"chat_{conversation.id}",
            {
                "type": "chat_closed",
                "conversation_id": conversation.id,
            }
        )

        return Response({"status": "closed"})
    except Conversation.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

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
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            "admins",
            {
                "type": "new_conversation",
                "conversation": {
                    "id": conversation.id,
                    "email": conversation.user_email,
                }
            }
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

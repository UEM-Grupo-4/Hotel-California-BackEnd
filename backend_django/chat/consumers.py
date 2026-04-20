import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Message, Conversation
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        sender = data["sender"]

        conversation = await database_sync_to_async(Conversation.objects.get)(id=self.conversation_id)

        if conversation.is_closed:
            return

        msg = await database_sync_to_async(Message.objects.create)(
            conversation=conversation,
            content=message,
            sender=sender,
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": msg.content,
                "sender": msg.sender,
            }
        )

    async def chat_closed(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat_closed",
            "conversation_id": event["conversation_id"],
        }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def save_message(self, message, sender):
        conversation = Conversation.objects.get(id=self.conversation_id)

        return Message.objects.create(
            conversation=conversation,
            content=message,
            sender=sender,
        )

class AdminConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("admins", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("admins", self.channel_name)

    async def new_conversation(self, event):
        await self.send(text_data=json.dumps({
            "type": "new_conversation",
            "conversation": event["conversation"]
        }))

    async def chat_closed(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat_closed",
            "conversation_id": event["conversation_id"],
        }))

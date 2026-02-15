import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from manage_service.models import ServiceRequest
from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.request_id = self.scope['url_route']['kwargs']['request_id']
        self.user = self.scope["user"]

        # Reject anonymous users
        if self.user.is_anonymous:
            await self.close()
            return

        # Get ServiceRequest safely (async-safe)
        try:
            service_request = await sync_to_async(ServiceRequest.objects.get)(
                id=self.request_id
            )
        except ServiceRequest.DoesNotExist:
            await self.close()
            return

        # Fetch related users safely (IMPORTANT FIX)
        customer = await sync_to_async(lambda: service_request.customer.user)()
        provider = await sync_to_async(
            lambda: service_request.provider_service.provider.user
        )()

        # Allow only booking participants
        if self.user != customer and self.user != provider:
            await self.close()
            return

        # Create or get conversation (one per request)
        self.conversation, created = await sync_to_async(
            Conversation.objects.get_or_create
        )(
            service_request=service_request
        )

        # Create room group
        self.room_group_name = f"chat_request_{self.request_id}"

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
        message = data.get("message")

        if not message:
            return

        # Save message safely
        await sync_to_async(Message.objects.create)(
            conversation=self.conversation,
            sender=self.user,
            content=message
        )

        # Broadcast message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": self.user.username,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
        }))

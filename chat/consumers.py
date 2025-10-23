# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        print(f"[WebSocket] Connect attempt by: {self.user}")
        
        if not self.user.is_authenticated:
            print("[WebSocket] User not authenticated, closing")
            await self.close()
            return
            
        self.other_user_id = self.scope['url_route']['kwargs']['user_id']
        
        # Create a unique room name
        user_ids = sorted([self.user.id, int(self.other_user_id)])
        self.room_name = f"chat_{user_ids[0]}_{user_ids[1]}"
        self.room_group_name = self.room_name
        
        print(f"[WebSocket] Joining room: {self.room_group_name}")
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        print(f"[WebSocket] Connection ACCEPTED for room: {self.room_group_name}")

    async def disconnect(self, close_code):
        print(f"[WebSocket] Disconnect: {close_code}")
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get("message", "").strip()
            receiver_id = data.get("receiver_id")
            
            print(f"[WebSocket] Received: '{message}' to user {receiver_id}")
            
            if not message or not receiver_id:
                return
            
            receiver = await self.get_user(receiver_id)
            if not receiver:
                return
            
            msg_obj = await self.create_message(self.user, receiver, message)
            
            # Broadcast to room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": self.user.username,
                    "sender_id": self.user.id,
                    "receiver": receiver.username,
                    "timestamp": msg_obj.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        except Exception as e:
            print(f"[WebSocket] Error in receive: {e}")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "sender_id": event["sender_id"],
            "receiver": event["receiver"],
            "timestamp": event.get("timestamp", "")
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def create_message(self, sender, receiver, text):
        return Message.objects.create(
            sender=sender,
            receiver=receiver,
            text=text
        )
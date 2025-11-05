from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import json

class DashboardConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
            return

        self.room_group_name = f'dashboard_{self.user.id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive_json(self, content):
        message_type = content.get('type')
        if message_type == 'ping':
            await self.send_json({'type': 'pong'})

    async def dashboard_update(self, event):
        await self.send_json(event['data'])

class MissionConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
            return

        self.mission_id = self.scope['url_route']['kwargs']['mission_id']
        self.room_group_name = f'mission_{self.mission_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive_json(self, content):
        message_type = content.get('type')
        if message_type == 'ping':
            await self.send_json({'type': 'pong'})

    async def mission_update(self, event):
        await self.send_json(event['data'])

    async def participant_verified(self, event):
        await self.send_json(event['data'])

class AuditConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
            return

        self.audit_id = self.scope['url_route']['kwargs']['audit_id']
        self.room_group_name = f'audit_{self.audit_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive_json(self, content):
        message_type = content.get('type')
        if message_type == 'ping':
            await self.send_json({'type': 'pong'})

    async def audit_status_changed(self, event):
        await self.send_json(event['data'])

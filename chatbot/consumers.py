import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        time = data['time']

        # Envía el mensaje de notificación al frontend
        await self.send(text_data=json.dumps({
            'message': message,
            'time': time
        }))
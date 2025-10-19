import json
from channels.generic.websocket import AsyncWebsocketConsumer

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("orders_group", self.channel_name)
        await self.accept()
        print("🔗 Cliente conectado al WebSocket")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("orders_group", self.channel_name)

    async def send_new_order(self, event):
        await self.send(text_data=json.dumps({
            "type": "new_order",
            "data": event["data"]
        }))

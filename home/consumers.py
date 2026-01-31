# import json
# from channels.generic.websocket import AsyncWebsocketConsumer

# class NotificationConsumer(AsyncWebsocketConsumer):
#     print("Consumerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
#     async def connect(self):
#         # Join the notifications group
#         await self.channel_layer.group_add(
#             "notifications",
#             self.channel_name
#         )
#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave the notifications group
#         await self.channel_layer.group_discard(
#             "notifications",
#             self.channel_name
#         )

#     # Receive message from group
#     async def send_notification(self, event):
#         message = event['message']
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message
#         }))

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user_group = None
        user = self.scope.get("user")

        if not user or not user.is_authenticated:
            await self.close(code=403)
            return

        self.user_group = f"user_{user.id}"

        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )

        await self.accept()


        await self.send(text_data=json.dumps({
            "type": "connection",
            "message": "Connected successfully"
        }))

    async def disconnect(self, close_code):
        # 🔥 SAFE CHECK
        if self.user_group:
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )

    async def notify(self, event):
        await self.send(text_data=json.dumps({
            "id": event["id"],
            "title": event["title"],
            "message": event["message"],
            "notification_type": event["notification_type"],
            "project_id": event["project_id"],
            "task_id": event["task_id"],
            "created_at": event["created_at"],
        }))

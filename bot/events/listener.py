import json


class Event:
    def __init__(self, bot, name):
        self.bot = bot
        self.name = name


class EventListener:
    def __init__(self, events: list[Event], pubsub):
        self.events = events
        self.pubsub = pubsub

    async def dispatch(self, event, *args, **kwargs):
        for e in self.events:
            if e.name == event:
                await e.callback(*args, **kwargs)

    async def listen(self):
        message = self.pubsub.get_message()
        while message is not None:
            if message["type"] == "pmessage":
                data = message.get("data")
                if data is None:
                    return
                data = data.decode("utf-8")
                data = json.loads(data)
                event = data.get("event")
                if not event:
                    return
                await self.dispatch(event, data)
            message = self.pubsub.get_message()

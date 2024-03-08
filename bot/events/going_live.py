from bot.events.listener import Event


class OnGoingLiveEvent(Event):
    async def callback(self, data):
        print("Going live event")
        print(data)

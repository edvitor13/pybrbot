from .async_loop import AsyncLoop
from .async_fast import AsyncFast
from .database import Database
from .bot_loading import BotLoading

class Tools:
    class AsyncLoop(AsyncLoop):
        pass

    class AsyncFast(AsyncFast):
        pass

    class BotLoading(BotLoading):
        pass

    class Database(Database):
        pass
import asyncio
from taskiq_redis import ListQueueBroker
from core.config import settings

# ListQueueBroker is the standard, stable implementation for Redis queues in TaskIQ
broker = ListQueueBroker("redis://localhost:6379")

async def init_broker():
    await broker.startup()

async def close_broker():
    await broker.shutdown()

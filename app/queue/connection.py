from redis import Redis
from rq import Queue
from ..core.config import settings

redis_conn = Redis(host=settings.redis_host, port=settings.redis_port)
queue = Queue(connection=redis_conn)

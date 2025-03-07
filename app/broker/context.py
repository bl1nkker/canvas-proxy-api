import contextvars

redis_client_var = contextvars.ContextVar("redis_client", default=None)

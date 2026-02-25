from contextvars import ContextVar
from uuid import uuid4


request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="-")


def get_request_id() -> str:
    return request_id_ctx_var.get()


def new_request_id() -> str:
    return str(uuid4())

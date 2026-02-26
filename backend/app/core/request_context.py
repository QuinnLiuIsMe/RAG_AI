from contextvars import ContextVar
from uuid import uuid4


request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="-")
trace_id_ctx_var: ContextVar[str] = ContextVar("trace_id", default="-")


def get_request_id() -> str:
    return request_id_ctx_var.get()


def new_request_id() -> str:
    return str(uuid4())


def get_trace_id() -> str:
    return trace_id_ctx_var.get()


def new_trace_id() -> str:
    return uuid4().hex

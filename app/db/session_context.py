from collections import deque
from contextlib import contextmanager
from typing import Dict

__scopes: Dict[int, deque] = {}


def __enter_scope(session):
    _id = id(session)
    if _id not in __scopes:
        __scopes[_id] = deque()

    __scopes[_id].append(True)


def __exit_scope(session):
    _id = id(session)
    if _id not in __scopes:
        return

    __scopes[_id].popleft()
    if len(__scopes[_id]) == 0:
        __delete_scope(session)


def __delete_scope(session):
    _id = id(session)
    if _id not in __scopes:
        return

    del __scopes[_id]


def __has_scope(session):
    _id = id(session)
    return _id in __scopes


@contextmanager
def session_context(session, autoclose: bool = False):
    try:
        if __has_scope(session):
            session.begin_nested()

        __enter_scope(session)
        yield session
        __exit_scope(session)
        session.commit()
    except Exception:
        __exit_scope(session)
        session.rollback()
        raise
    finally:
        if not __has_scope(session) and autoclose:
            session.close()

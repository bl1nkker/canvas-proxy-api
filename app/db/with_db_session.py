from functools import wraps

from sqlalchemy.orm import Session

from db.get_db_session import get_db_session


def with_db_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        db_session: Session = next(get_db_session())
        return func(db_session, *args, **kwargs)

    return wrapper

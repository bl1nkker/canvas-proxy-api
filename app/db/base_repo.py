from abc import ABC
from db.session_context import session_context


class BaseRepo(ABC):
    def __init__(self, session):
        self._session = session

    def session(self):
        return session_context(self._session)

from db.session_context import session_context


class BaseRepo:
    def __init__(self, session):
        self._session = session

    def session(self):
        return session_context(self._session)

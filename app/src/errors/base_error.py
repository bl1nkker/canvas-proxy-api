class BaseError(Exception):
    def __init__(
        self, *, message: str, code: str,
        data: dict | None = None
    ) -> None:
        super().__init__()
        self.message = message
        self.code = code
        self.data = data

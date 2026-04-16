class HolidaysApiError(Exception):
    """Raised when the API returns a non-2xx response."""

    def __init__(self, message: str, status_code: int, body: bytes) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body

    def __repr__(self) -> str:
        return f"HolidaysApiError(status_code={self.status_code}, message={str(self)!r})"

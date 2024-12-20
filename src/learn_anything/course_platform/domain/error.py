# Application generic error
class ApplicationError(Exception):
    @property
    def message(self) -> str:
        raise NotImplementedError


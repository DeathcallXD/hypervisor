from fastapi import HTTPException

class HttpExceptionDetail(HTTPException):
    def __init__(self, error_code: str, message: str, status_code: int) -> None:
        self.error_code: str = error_code
        self.detail: dict = {
            "message": message,
            "error_code": error_code
        }

        super().__init__(status_code=status_code, detail=self.detail)

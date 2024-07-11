from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException # pants: no-infer-dep


class ExceptionHandler:
    @staticmethod
    async def handle_exception(request, exc):
        if isinstance(exc, StarletteHTTPException):
            return await ExceptionHandler.handle_http_exception(request, exc)
        elif isinstance(exc, RequestValidationError):
            return await ExceptionHandler.handle_validation_exception(request, exc)
        # Add more elif blocks for additional exception types if needed
        else:
            # Handle generic or unhandled exceptions
            return await ExceptionHandler.handle_generic_exception(request, exc)

    @staticmethod
    async def handle_http_exception(request, exc: StarletteHTTPException):
        detail = exc.detail
        error_code, message = None, None
        if isinstance(detail, dict):
            error_code  = detail.get("error_code")
            message     = detail.get("message")

        d = {
            "error": {
                "error_code": error_code or 400,
                "message": message or exc.detail,
                "details": {},
                "validation_errors": [],
            }
        }
        return JSONResponse(content=jsonable_encoder(d), status_code=exc.status_code)

    @staticmethod
    async def handle_validation_exception(request, exc: RequestValidationError):
        d = {
            "error": {
                "code": 422,
                "message": "invalid request",
                "details": "",
                "validation_errors": exc.errors(),
                "body": exc.body,
            }
        }
        return JSONResponse(content=jsonable_encoder(d), status_code=422)

    @staticmethod
    async def handle_generic_exception(request, exc):
        d = {
            "error": {
                "code": 500,
                "message": f"{repr(exc)}",
                "details": f"exception type: {type(exc)}",
                "validation_errors": [],
            }
        }
        return JSONResponse(content=jsonable_encoder(d), status_code=500)

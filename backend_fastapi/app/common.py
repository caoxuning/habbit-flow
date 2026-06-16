from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: int
    message: str
    data: object | None = None


class AppException(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code


def ok(data=None):
    return {"code": 200, "message": "success", "data": data}


def install_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(_: Request, exc: AppException):
        return JSONResponse(
            status_code=400 if exc.code != 401 else 401,
            content={"code": exc.code, "message": exc.message, "data": None},
        )

    @app.exception_handler(Exception)
    async def system_exception_handler(_: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": str(exc), "data": None},
        )

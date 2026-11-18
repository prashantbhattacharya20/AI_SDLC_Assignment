from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class DomainError(Exception):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class StateTransitionError(DomainError):
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class SelfApprovalError(DomainError):
    def __init__(self, detail: str = "Self-approval is strictly prohibited"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_exception_handler(_request: Request, exc: DomainError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_request: Request, exc: RequestValidationError):
        # Format validation error message cleanly
        errors = exc.errors()
        messages = []
        clean_errors = []
        for err in errors:
            loc = " -> ".join(str(item) for item in err.get("loc", []))
            msg = str(err.get("msg", "Validation error"))
            messages.append(f"{loc}: {msg}")

            clean_err = {k: v for k, v in err.items() if k != "ctx"}
            if "ctx" in err:
                clean_err["ctx"] = {k: str(v) for k, v in err["ctx"].items()}
            clean_errors.append(clean_err)

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"detail": "; ".join(messages), "errors": clean_errors}),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

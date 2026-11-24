"""422 doğrulama hatalarında gönderilen değeri yanıttan çıkarır. Sorumlu: Mert.

FastAPI varsayılan olarak hatalı alanın değerini `input` içinde geri döndürür;
parola alanı hatalıysa parola yanıtta görünür (sözleşme: şifre yanıtlarda bulunmaz).
`loc`, `msg` ve `type` korunur; frontend'in alan hatası gösterimi (toFieldErrors) değişmez.
"""

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

_HIDDEN_KEYS = {"input", "ctx"}


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [{key: value for key, value in error.items() if key not in _HIDDEN_KEYS} for error in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": jsonable_encoder(errors)})

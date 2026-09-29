from app.routers import auth, boards, tasks
app.include_router(auth.router)
app.include_router(boards.router)
app.include_router(tasks.router)
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Validation Error", "details": exc.errors()}
    )
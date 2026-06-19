from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.core.config import settings
from app.api.routes import health, docs

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


# --- Dynamic CORS that handles Vercel preview URLs ---
# Parse explicit origins from .env (strip trailing slashes)
raw_origins = settings.FRONTEND_URL.split(",")
explicit_origins = [origin.strip().rstrip("/") for origin in raw_origins if origin.strip()]


def is_allowed_origin(origin: str) -> bool:
    """Check if origin is allowed: exact match OR any *.vercel.app subdomain."""
    if not origin:
        return False
    # Exact match against configured origins
    if origin in explicit_origins:
        return True
    # Allow any Vercel preview deployment
    if origin.endswith(".vercel.app"):
        return True
    # Allow localhost for development
    if "localhost" in origin or "127.0.0.1" in origin:
        return True
    return False


class DynamicCORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware that dynamically checks origins,
    including Vercel preview deployment URLs."""

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin", "")

        # Handle preflight (OPTIONS) requests
        if request.method == "OPTIONS":
            if is_allowed_origin(origin):
                return Response(
                    status_code=200,
                    headers={
                        "Access-Control-Allow-Origin": origin,
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization",
                        "Access-Control-Allow-Credentials": "true",
                        "Access-Control-Max-Age": "3600",
                    },
                )
            return Response(status_code=403)

        # Handle normal requests
        response = await call_next(request)

        if is_allowed_origin(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

        return response


app.add_middleware(DynamicCORSMiddleware)

app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])
app.include_router(docs.router, prefix=f"{settings.API_V1_STR}/docs", tags=["docs"])

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

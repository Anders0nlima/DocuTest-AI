from fastapi import FastAPI
from app.core.config import settings
from app.api.routes import health, docs

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])
app.include_router(docs.router, prefix=f"{settings.API_V1_STR}/docs", tags=["docs"])

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import health, docs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# --- CORS Configuration ---
# In production, allow the Vercel frontend + any preview deployments.
# We use allow_origin_regex to match all *.vercel.app subdomains dynamically.
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS: Production mode — allowing all *.vercel.app origins")
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS: Development mode — allowing all origins")

app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])
app.include_router(docs.router, prefix=f"{settings.API_V1_STR}/docs", tags=["docs"])

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

from supabase import create_client, Client
from app.core.config import settings

def get_supabase() -> Client:
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError("Supabase credentials not configured in environment variables.")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

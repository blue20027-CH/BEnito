import os

from supabase import create_client, Client

SUPABASE_URL = os.getenv(
    "SUPABASE_URL",
    "https://tcezyirkglpihohuzrqo.supabase.co",
)
SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRjZXp5aXJrZ2xwaWhvaHV6cnFvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY2MzczMDYsImV4cCI6MjA5MjIxMzMwNn0.oTlKV86XE3Cq7MMRZyySzWoDYzv2OBcPpwAIpgq-Kwk",
)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

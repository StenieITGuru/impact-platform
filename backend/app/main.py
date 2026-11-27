from fastapi import FastAPI
from sqlalchemy import text

from app.api import auth, organizations
from app.core.database import engine

app = FastAPI(title="ImpactArc IPIS API", version="0.1.0")

app.include_router(auth.router)
app.include_router(organizations.router)


@app.get("/health", tags=["System"])
def health():
    with engine.connect() as conn:
        conn.execute(text("select 1"))
    return {"status": "ok", "database": "connected"}

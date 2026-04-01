from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.users_router import router as users_router
from db.db_pool import close_pool

app = FastAPI(
    title="Users Service",
    version="1.0.0",
    description="Handles user accounts, profiles, reputation, verification."
)

# CORS (Gateway → services)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # or restrict to gateway service
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(users_router, prefix="/users", tags=["Users"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "users-service-running"}

@app.on_event("shutdown")
async def shutdown_event():
    msg = await close_pool()
    return print(msg)

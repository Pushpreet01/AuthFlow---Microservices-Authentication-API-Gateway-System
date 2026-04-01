from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth_router import router as auth_router
from db.db_pool import init_pool, close_pool

app = FastAPI(
    title="Auth Service",
    version="1.0.0",
    description="Handles auth."
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
app.include_router(auth_router, prefix="/auth", tags=["Auth"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "auth-service-running"}

@app.on_event("startup")
async def startup():
    await init_pool()
    return print("Database pool initialized.")

@app.on_event("shutdown")
async def shutdown_event():
    msg = await close_pool()
    return print(msg)

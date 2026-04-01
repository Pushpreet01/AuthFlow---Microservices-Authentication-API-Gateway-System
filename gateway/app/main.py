from fastapi import FastAPI
from app.routes.auth_routes import router as auth_router
from app.routes.user_routes import router as user_router
from app.auth_middleware import AuthMiddleware

app = FastAPI(title="API Gateway")

app.add_middleware(AuthMiddleware)

app.include_router(auth_router)
app.include_router(user_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Badminton API Gateway"}

@app.get("/health")
async def health_check():
    return {"status": "API Gateway healthy"}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth

app = FastAPI(
    title="Authentication API",
    description="User authentication with email verification",
    version="1.0.0",
    servers=[{"url": "https://auth-api-nvdempim.fly.dev", "description": "Production server"}]
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(auth.router, tags=["认证"])

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

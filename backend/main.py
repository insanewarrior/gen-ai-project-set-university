import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from middleware.auth import CurrentUser, get_current_user

app = FastAPI(title="StrengthWise API")

# Allow localhost for dev and CloudFront for production; use "*" for MVP simplicity
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    os.getenv("CLOUDFRONT_URL", ""),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in ALLOWED_ORIGINS if o] or ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


# Reference implementation: how to protect endpoints with auth dependency.
# All future routers add Depends(get_current_user) to their path operations.
@app.get("/me")
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    return {"userId": current_user}


handler = Mangum(app)  # Lambda entry point

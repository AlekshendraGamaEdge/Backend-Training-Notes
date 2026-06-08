import logging
from fastapi import FastAPI, HTTPException, Request, Security
from fastapi.responses import Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.utils import get_openapi
from starlette.middleware.base import BaseHTTPMiddleware
from config import settings
from models import UserCreate, TokenResponse, UserResponse
from db import create_users, async_find_user
from auth import hash_password, verify_password, create_access_token, verify_jwt_token



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("main")


PUBLIC_PATHS = {"/register", "/docs", "/openapi.json", "/redoc", "/"}

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)
        
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning(f"Missing or invalid auth header for {request.url.path}")
            return Response("Unauthorized", status_code=401)
        
        token = auth_header.split(" ", 1)[1] 
        logger.info(f"Token extracted from header for {request.url.path}: {token[:20]}...")
        
        try:
            payload = await verify_jwt_token(token)
            email = payload.get("sub")
            logger.info(f"Token validated successfully for email: {email}")
            if not email:
                logger.warning("Token missing 'sub' claim")
                return Response("Unauthorized", status_code=401)

            user = await async_find_user(email)
            if not user:
                logger.warning(f"User not found for email: {email}")
                return Response("Unauthorized", status_code=401)

            request.state.user = user
            request.state.user_email = email
            logger.info(f"User loaded into request state: {email}")
        except HTTPException as e:
            logger.warning(f"Auth failed for {request.url.path}: {e.detail}")
            return Response(e.detail, status_code=e.status_code)

        response = await call_next(request)
        return response


app = FastAPI(title="JWT Auth Demo", version="3.0")

security = HTTPBearer()

app.add_middleware(JWTAuthMiddleware)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="JWT Auth Demo",
        version="3.0",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT Token"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


@app.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    existing = await async_find_user(user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = hash_password(user_data.password)
    await create_users(
        email=user_data.email,
        hashed_password=hashed_pw,
        full_name=user_data.full_name,
    )
    access_token = create_access_token(data={"sub": user_data.email})
    logger.info(f"User registered: {user_data.email}")
    return TokenResponse(access_token=access_token, token_type="bearer")


@app.get("/")
async def root():
    return {"status": "JWT auth server running", "public_paths": list(PUBLIC_PATHS)}


@app.get("/protected")
async def protected_route(request: Request, credentials: HTTPAuthorizationCredentials = Security(security)):
    user = request.state.user
    return {
        "message": f"Hello {user['full_name']}, you accessed a protected resource!",
        "user_email": user["email"],
        "registered_at": user["created_at"],
    }


@app.get("/me", response_model=UserResponse)
async def get_me(request: Request, credentials: HTTPAuthorizationCredentials = Security(security)):
    user = request.state.user
    return UserResponse(
        email=user["email"],
        full_name=user["full_name"],
        created_at=user["created_at"],
    )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
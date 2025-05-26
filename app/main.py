# from fastapi import FastAPI
# from app.routers import auth

# from app.core.dependencies import get_current_user
# from fastapi import Depends
# from app.models.user import User

# from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
# from fastapi.security import OAuth2

# class OAuth2PasswordBearerWithCookie(OAuth2):
#     def __init__(self, tokenUrl: str):
#         flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl})
#         super().__init__(flows=flows)

# app = FastAPI(title="Lu Estilo API")
# app.include_router(auth.router)

# @app.get("/")
# def read_root():
#     return {"message": "API da Lu Estilo está no ar!"}

# @app.get("/me")
# def read_current_user(user: User = Depends(get_current_user)):
#     return {"id": user.id, "name": user.name, "email": user.email, "role": user.role.value}

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.routers import auth

app = FastAPI(title="Lu Estilo API")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Lu Estilo API",
        version="1.0.0",
        description="API protegida com JWT",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(auth.router)
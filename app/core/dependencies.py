from fastapi import Depends, HTTPException, status
from app.core.auth_scheme import OAuth2PasswordBearerWithCookie
from jose import JWTError
from sqlalchemy.orm import Session
from app.db.connection import SessionLocal
from app.models.user import User
from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = decode_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
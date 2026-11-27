from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])
bearer = HTTPBearer(auto_error=False)


class Registration(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=6, max_length=128)


class Login(BaseModel):
    username: str
    password: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
):
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(401, "Brak tokenu")
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(401, "Nieprawidłowy lub wygasły token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(401, "Użytkownik nie istnieje")
    return user


@router.post("/register")
def register(payload: Registration, db: Session = Depends(get_db)):
    username = payload.username.strip()
    email = payload.email.strip().lower()
    if len(username) < 3 or "@" not in email:
        raise HTTPException(400, "Nieprawidłowa nazwa użytkownika lub e-mail")
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(409, "Nazwa użytkownika jest zajęta")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "E-mail jest zajęty")
    try:
        password_hash = hash_password(payload.password)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    user = User(username=username, email=email, password_hash=password_hash)
    db.add(user)
    db.commit()
    return {"message": "Konto utworzone", "username": username}


@router.post("/login")
def login(payload: Login, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Nieprawidłowy login lub hasło")
    return {"access_token": create_access_token(user.id),
            "token_type": "bearer", "username": user.username}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "email": user.email}

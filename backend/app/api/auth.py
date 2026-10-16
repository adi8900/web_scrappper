from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Header,
)

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

from app.models.user import User


router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def get_current_user(
    authorization: str = Header(
        default=None
    ),
    db: Session = Depends(get_db),
):

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Brak tokenu",
        )

    if not authorization.startswith(
        "Bearer "
    ):
        raise HTTPException(
            status_code=401,
            detail="Nieprawidłowy token",
        )

    token = authorization[
        7:
    ]

    user_id = decode_access_token(
        token
    )

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Token wygasł lub jest nieprawidłowy",
        )

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Użytkownik nie istnieje",
        )

    return user


@router.post("/register")
async def register(
    username: str,
    email: str,
    password: str,
    db: Session = Depends(get_db),
):

    username = username.strip()
    email = email.strip().lower()

    if len(username) < 3:
        raise HTTPException(
            status_code=400,
            detail="Nazwa użytkownika musi mieć co najmniej 3 znaki",
        )

    if len(password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Hasło musi mieć co najmniej 6 znaków",
        )

    existing_username = (
        db.query(User)
        .filter(
            User.username == username
        )
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Nazwa użytkownika jest już zajęta",
        )

    existing_email = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email jest już zajęty",
        )

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(
            password
        ),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Konto utworzone",
        "username": user.username,
    }


@router.post("/login")
async def login(
    username: str,
    password: str,
    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(
            User.username == username
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Nieprawidłowy login lub hasło",
        )

    if not verify_password(
        password,
        user.password_hash,
    ):

        raise HTTPException(
            status_code=401,
            detail="Nieprawidłowy login lub hasło",
        )

    token = create_access_token(
        user.id
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
    }


@router.get("/me")
async def me(
    user: User = Depends(
        get_current_user
    ),
):

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }
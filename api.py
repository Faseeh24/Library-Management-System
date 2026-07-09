import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
from models import Book, Loan, Member, User


app = FastAPI(
    title="Library Management API",
    description="Backend API for Library Management System",
    version="1.0",
)

Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "library-management-secret")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
PASSWORD_ITERATIONS = int(os.getenv("PASSWORD_ITERATIONS", "100000"))
PRIVILEGED_REGISTRATION_CODE = os.getenv("PRIVILEGED_REGISTRATION_CODE")


class UserRole(str, Enum):
    admin = "admin"
    librarian = "librarian"
    member = "member"


class BookCreate(BaseModel):
    title: str
    author: str


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None


class MemberCreate(BaseModel):
    name: str


class MemberUpdate(BaseModel):
    name: Optional[str] = None


class LoanCreate(BaseModel):
    book_id: int
    member_id: int


class LoanUpdate(BaseModel):
    book_id: Optional[int] = None
    member_id: Optional[int] = None


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: UserRole = UserRole.member
    registration_code: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    role: str


# Database dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _serialize_book(book: Book):
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
    }


def _serialize_member(member: Member):
    return {
        "id": member.id,
        "name": member.name,
    }


def _serialize_loan(loan: Loan):
    return {
        "id": loan.id,
        "book_id": loan.book_id,
        "member_id": loan.member_id,
    }


def _serialize_user(user: User):
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
    }


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    ).hex()
    return f"{salt}${password_hash}"


def _verify_password(password: str, stored_value: str) -> bool:
    try:
        salt, expected_hash = stored_value.split("$", 1)
    except ValueError:
        return False

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    ).hex()
    return hmac.compare_digest(password_hash, expected_hash)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _create_access_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "exp": int(
            (
                datetime.now(timezone.utc)
                + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            ).timestamp()
        ),
    }
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )
    payload_segment = _b64url_encode(payload_bytes)
    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        payload_segment.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    signature_segment = _b64url_encode(signature)
    return f"{payload_segment}.{signature_segment}"


def _decode_access_token(token: str):
    try:
        payload_segment, signature_segment = token.split(".", 1)
        expected_signature = hmac.new(
            SECRET_KEY.encode("utf-8"),
            payload_segment.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        provided_signature = _b64url_decode(signature_segment)
        if not hmac.compare_digest(expected_signature, provided_signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = json.loads(_b64url_decode(payload_segment))
        exp = int(payload.get("exp", 0))
        if datetime.now(timezone.utc).timestamp() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    payload = _decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_roles(*allowed_roles: str):
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return dependency


def _get_book_or_404(db: Session, book_id: int) -> Book:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


def _get_member_or_404(db: Session, member_id: int) -> Member:
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


def _get_loan_or_404(db: Session, loan_id: int) -> Loan:
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan


# Authentication endpoints

@app.post("/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == payload.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    if payload.role != UserRole.member:
        user_count = db.query(User).count()
        if user_count > 0 and payload.registration_code != PRIVILEGED_REGISTRATION_CODE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privileged roles require a valid registration code",
            )

    user = User(
        username=payload.username,
        password_hash=_hash_password(payload.password),
        role=payload.role.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _serialize_user(user)


@app.post("/auth/login", response_model=TokenResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not _verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return TokenResponse(access_token=_create_access_token(user))


@app.get("/auth/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return _serialize_user(current_user)


# Book endpoints

@app.get("/books")
def get_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    return [_serialize_book(book) for book in books]


@app.get("/books/search")
def search_books(
    title: Optional[str] = Query(None, description="Search book by title"),
    db: Session = Depends(get_db),
):
    query = db.query(Book)

    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))

    books = query.all()
    return [_serialize_book(book) for book in books]


@app.get("/books/{book_id}")
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = _get_book_or_404(db, book_id)
    return _serialize_book(book)


@app.post("/books", status_code=status.HTTP_201_CREATED)
def create_book(
    payload: BookCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "librarian")),
):
    book = Book(title=payload.title, author=payload.author)
    db.add(book)
    db.commit()
    db.refresh(book)
    return _serialize_book(book)


@app.put("/books/{book_id}")
def update_book(
    book_id: int,
    payload: BookUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "librarian")),
):
    book = _get_book_or_404(db, book_id)
    if payload.title is not None:
        book.title = payload.title
    if payload.author is not None:
        book.author = payload.author
    db.commit()
    db.refresh(book)
    return _serialize_book(book)


@app.delete("/books/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "librarian")),
):
    book = _get_book_or_404(db, book_id)
    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully"}


# Member endpoints

@app.get("/members")
def get_members(db: Session = Depends(get_db)):
    members = db.query(Member).all()
    return [_serialize_member(member) for member in members]


@app.get("/members/{member_id}")
def get_member(member_id: int, db: Session = Depends(get_db)):
    member = _get_member_or_404(db, member_id)
    return _serialize_member(member)


@app.post("/members", status_code=status.HTTP_201_CREATED)
def create_member(
    payload: MemberCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "librarian")),
):
    member = Member(name=payload.name)
    db.add(member)
    db.commit()
    db.refresh(member)
    return _serialize_member(member)


@app.put("/members/{member_id}")
def update_member(
    member_id: int,
    payload: MemberUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "librarian")),
):
    member = _get_member_or_404(db, member_id)
    if payload.name is not None:
        member.name = payload.name
    db.commit()
    db.refresh(member)
    return _serialize_member(member)


@app.delete("/members/{member_id}")
def delete_member(
    member_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "librarian")),
):
    member = _get_member_or_404(db, member_id)
    db.delete(member)
    db.commit()
    return {"message": "Member deleted successfully"}


# Loan endpoints

@app.get("/loans")
def get_loans(db: Session = Depends(get_db)):
    loans = db.query(Loan).all()
    return [_serialize_loan(loan) for loan in loans]


@app.get("/loans/{loan_id}")
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = _get_loan_or_404(db, loan_id)
    return _serialize_loan(loan)


@app.post("/loans", status_code=status.HTTP_201_CREATED)
def create_loan(
    payload: LoanCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "librarian")),
):
    _get_book_or_404(db, payload.book_id)
    _get_member_or_404(db, payload.member_id)

    loan = Loan(book_id=payload.book_id, member_id=payload.member_id)
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return _serialize_loan(loan)


@app.put("/loans/{loan_id}")
def update_loan(
    loan_id: int,
    payload: LoanUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "librarian")),
):
    loan = _get_loan_or_404(db, loan_id)

    if payload.book_id is not None:
        _get_book_or_404(db, payload.book_id)
        loan.book_id = payload.book_id
    if payload.member_id is not None:
        _get_member_or_404(db, payload.member_id)
        loan.member_id = payload.member_id

    db.commit()
    db.refresh(loan)
    return _serialize_loan(loan)


@app.delete("/loans/{loan_id}")
def delete_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "librarian")),
):
    loan = _get_loan_or_404(db, loan_id)
    db.delete(loan)
    db.commit()
    return {"message": "Loan deleted successfully"}

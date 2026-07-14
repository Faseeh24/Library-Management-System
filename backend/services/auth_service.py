import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, AUTH_SECRET_KEY, PASSWORD_ITERATIONS, PRIVILEGED_REGISTRATION_CODE
from backend.repositories.user_repository import count_users, create_user, get_user_by_username
from backend.schemas import LoginRequest, RegisterRequest


def hash_password(password: str) -> str:
    salt = hashlib.sha256(str(datetime.now(timezone.utc).timestamp()).encode('utf-8')).hexdigest()[:32]
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        PASSWORD_ITERATIONS,
    ).hex()
    return f'{salt}${password_hash}'


def verify_password(password: str, stored_value: str) -> bool:
    try:
        salt, expected_hash = stored_value.split('$', 1)
    except ValueError:
        return False

    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        PASSWORD_ITERATIONS,
    ).hex()
    return hmac.compare_digest(password_hash, expected_hash)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')


def _b64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(user) -> str:
    payload = {
        'sub': str(user.id),
        'username': user.username,
        'role': user.role,
        'exp': int((datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
    }
    payload_bytes = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8')
    payload_segment = _b64url_encode(payload_bytes)
    signature = hmac.new(
        AUTH_SECRET_KEY.encode('utf-8'),
        payload_segment.encode('utf-8'),
        hashlib.sha256,
    ).digest()
    return f'{payload_segment}.{_b64url_encode(signature)}'


def decode_access_token(token: str):
    try:
        payload_segment, signature_segment = token.split('.', 1)
        expected_signature = hmac.new(
            AUTH_SECRET_KEY.encode('utf-8'),
            payload_segment.encode('utf-8'),
            hashlib.sha256,
        ).digest()
        provided_signature = _b64url_decode(signature_segment)
        if not hmac.compare_digest(expected_signature, provided_signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid authentication token',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        payload = json.loads(_b64url_decode(payload_segment))
        if datetime.now(timezone.utc).timestamp() > int(payload.get('exp', 0)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token has expired',
                headers={'WWW-Authenticate': 'Bearer'},
            )
        return payload
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication token',
            headers={'WWW-Authenticate': 'Bearer'},
        ) from exc


def register_account(db: Session, payload: RegisterRequest):
    if get_user_by_username(db, payload.username):
        raise HTTPException(status_code=400, detail='Username already exists')

    if payload.role.value != 'member':
        if count_users(db) > 0 and payload.registration_code != PRIVILEGED_REGISTRATION_CODE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Privileged roles require a valid registration code',
            )

    user = create_user(db, payload.username, hash_password(payload.password), payload.role.value)
    return user


def authenticate_user(db: Session, payload: LoginRequest):
    user = get_user_by_username(db, payload.username)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Invalid username or password')
    return user

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.routes.deps import get_current_user, get_db
from backend.schemas import LoginRequest, RegisterRequest, TokenResponse, UserOut
from backend.services.auth_service import authenticate_user, create_access_token, register_account

router = APIRouter(prefix='/auth', tags=['Authentication'])


@router.post('/register', response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = register_account(db, payload)
    return {'id': user.id, 'username': user.username, 'role': user.role}


@router.post('/login', response_model=TokenResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload)
    return TokenResponse(access_token=create_access_token(user))


@router.get('/me', response_model=UserOut)
def read_current_user(current_user=Depends(get_current_user)):
    return {'id': current_user.id, 'username': current_user.username, 'role': current_user.role}

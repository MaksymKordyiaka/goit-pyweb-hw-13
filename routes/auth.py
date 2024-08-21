from fastapi import APIRouter, HTTPException, status, Depends, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from schemas import UserCreate, UserResponse, TokenModel
from db.connect_db import get_db
from services.auth import auth_services
from repository.users import get_user_by_email, create_user, update_token

router = APIRouter()
security = HTTPBearer()


@router.post('/register', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    exist_user = get_user_by_email(db, user.email)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='email already registered')

    user.password = auth_services.hash_password(user.password)
    new_user = create_user(db, user)
    return new_user


@router.post('/login', response_model=TokenModel, status_code=status.HTTP_201_CREATED)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email(db, form_data.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_services.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    access_token = auth_services.create_access_token(data={'sub': user.email})
    refresh_token = auth_services.create_refresh_token(data={'sub': user.email})
    update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel, status_code=status.HTTP_201_CREATED)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = auth_services.decode_refresh_token(token)
    user = get_user_by_email(db, email)
    if user.refresh_token != token:
        update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = auth_services.create_access_token(data={"sub": email})
    refresh_token = auth_services.create_refresh_token(data={"sub": email})
    update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

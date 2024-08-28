from libgravatar import Gravatar
from sqlalchemy.orm import Session
from db.models import User
from schemas import UserCreate


def get_user_by_email(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate) -> User:
    avatar = None
    try:
        g = Gravatar(user.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**user.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_token(user: User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()


def confirmed_email(email: str, db: Session) -> None:
    user = get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


def update_avatar(email, url: str, db: Session) -> User:
    user = get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user

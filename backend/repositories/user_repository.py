from sqlalchemy.orm import Session

from backend import models


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def count_users(db: Session):
    return db.query(models.User).count()


def create_user(db: Session, username: str, password_hash: str, role: str):
    user = models.User(username=username, password_hash=password_hash, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

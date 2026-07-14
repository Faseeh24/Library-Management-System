from sqlalchemy.orm import Session

from backend import models
from backend.schemas import MemberCreate, MemberUpdate


def list_members(db: Session):
    return db.query(models.Member).all()


def get_member(db: Session, member_id: int):
    return db.query(models.Member).filter(models.Member.id == member_id).first()


def create_member(db: Session, payload: MemberCreate):
    member = models.Member(name=payload.name)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def update_member(db: Session, member: models.Member, payload: MemberUpdate):
    if payload.name is not None:
        member.name = payload.name
    db.commit()
    db.refresh(member)
    return member


def delete_member(db: Session, member: models.Member):
    db.delete(member)
    db.commit()

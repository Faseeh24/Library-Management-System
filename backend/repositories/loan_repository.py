from sqlalchemy.orm import Session

from backend import models
from backend.schemas import LoanCreate, LoanUpdate


def list_loans(db: Session):
    return db.query(models.Loan).all()


def get_loan(db: Session, loan_id: int):
    return db.query(models.Loan).filter(models.Loan.id == loan_id).first()


def create_loan(db: Session, payload: LoanCreate):
    loan = models.Loan(book_id=payload.book_id, member_id=payload.member_id)
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def update_loan(db: Session, loan: models.Loan, payload: LoanUpdate):
    if payload.book_id is not None:
        loan.book_id = payload.book_id
    if payload.member_id is not None:
        loan.member_id = payload.member_id
    db.commit()
    db.refresh(loan)
    return loan


def delete_loan(db: Session, loan: models.Loan):
    db.delete(loan)
    db.commit()

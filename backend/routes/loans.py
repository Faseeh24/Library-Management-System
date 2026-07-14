from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.routes.deps import get_db, require_roles
from backend.repositories import loan_repository as repo
from backend.schemas import LoanCreate, LoanUpdate

router = APIRouter(prefix='/loans', tags=['Loans'])


def _serialize(loan):
    return {'id': loan.id, 'book_id': loan.book_id, 'member_id': loan.member_id}


@router.get('')
def get_loans(db: Session = Depends(get_db)):
    return [_serialize(loan) for loan in repo.list_loans(db)]


@router.get('/{loan_id}')
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = repo.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail='Loan not found')
    return _serialize(loan)


@router.post('', status_code=status.HTTP_201_CREATED)
def create_loan(payload: LoanCreate, db: Session = Depends(get_db), _: object = Depends(require_roles('admin', 'librarian', 'member'))):
    return _serialize(repo.create_loan(db, payload))


@router.put('/{loan_id}')
def update_loan(loan_id: int, payload: LoanUpdate, db: Session = Depends(get_db), _: object = Depends(require_roles('admin', 'librarian', 'member'))):
    loan = repo.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail='Loan not found')
    return _serialize(repo.update_loan(db, loan, payload))


@router.delete('/{loan_id}')
def delete_loan(loan_id: int, db: Session = Depends(get_db), _: object = Depends(require_roles('admin', 'librarian', 'member'))):
    loan = repo.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail='Loan not found')
    repo.delete_loan(db, loan)
    return {'message': 'Loan deleted successfully'}

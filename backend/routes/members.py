from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.routes.deps import get_db, require_roles
from backend.repositories import member_repository as repo
from backend.schemas import MemberCreate, MemberUpdate

router = APIRouter(prefix='/members', tags=['Members'])


def _serialize(member):
    return {'id': member.id, 'name': member.name}


@router.get('')
def get_members(db: Session = Depends(get_db)):
    return [_serialize(member) for member in repo.list_members(db)]


@router.get('/{member_id}')
def get_member(member_id: int, db: Session = Depends(get_db)):
    member = repo.get_member(db, member_id)
    if not member:
        raise HTTPException(status_code=404, detail='Member not found')
    return _serialize(member)


@router.post('', status_code=status.HTTP_201_CREATED)
def create_member(payload: MemberCreate, db: Session = Depends(get_db), _: object = Depends(require_roles('admin', 'librarian'))):
    return _serialize(repo.create_member(db, payload))


@router.put('/{member_id}')
def update_member(member_id: int, payload: MemberUpdate, db: Session = Depends(get_db), _: object = Depends(require_roles('admin', 'librarian'))):
    member = repo.get_member(db, member_id)
    if not member:
        raise HTTPException(status_code=404, detail='Member not found')
    return _serialize(repo.update_member(db, member, payload))


@router.delete('/{member_id}')
def delete_member(member_id: int, db: Session = Depends(get_db), _: object = Depends(require_roles('admin', 'librarian'))):
    member = repo.get_member(db, member_id)
    if not member:
        raise HTTPException(status_code=404, detail='Member not found')
    repo.delete_member(db, member)
    return {'message': 'Member deleted successfully'}

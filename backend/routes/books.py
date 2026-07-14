from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.routes.deps import get_db, require_roles
from backend.repositories import book_repository as repo
from backend.schemas import BookCreate, BookUpdate

router = APIRouter(prefix='/books', tags=['Books'])


def _serialize(book):
    return {'id': book.id, 'title': book.title, 'author': book.author}


@router.get('')
def get_books(db: Session = Depends(get_db)):
    return [_serialize(book) for book in repo.list_books(db)]


@router.get('/search')
def search_books(title: str | None = Query(None, description='Search book by title'), db: Session = Depends(get_db)):
    return [_serialize(book) for book in repo.search_books_by_title(db, title or '')]


@router.get('/{book_id}')
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = repo.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail='Book not found')
    return _serialize(book)


@router.post('', status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate, db: Session = Depends(get_db), _: object = Depends(require_roles('admin', 'librarian'))):
    return _serialize(repo.create_book(db, payload))


@router.put('/{book_id}')
def update_book(book_id: int, payload: BookUpdate, db: Session = Depends(get_db), _: object = Depends(require_roles('admin', 'librarian'))):
    book = repo.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail='Book not found')
    return _serialize(repo.update_book(db, book, payload))


@router.delete('/{book_id}')
def delete_book(book_id: int, db: Session = Depends(get_db), _: object = Depends(require_roles('admin', 'librarian'))):
    book = repo.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail='Book not found')
    repo.delete_book(db, book)
    return {'message': 'Book deleted successfully'}

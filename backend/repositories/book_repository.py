from sqlalchemy.orm import Session

from backend import models
from backend.schemas import BookCreate, BookUpdate


def list_books(db: Session):
    return db.query(models.Book).all()


def search_books_by_title(db: Session, title: str):
    query = db.query(models.Book)
    if title:
        query = query.filter(models.Book.title.ilike(f'%{title}%'))
    return query.all()


def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()


def create_book(db: Session, payload: BookCreate):
    book = models.Book(title=payload.title, author=payload.author)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def update_book(db: Session, book: models.Book, payload: BookUpdate):
    if payload.title is not None:
        book.title = payload.title
    if payload.author is not None:
        book.author = payload.author
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book: models.Book):
    db.delete(book)
    db.commit()

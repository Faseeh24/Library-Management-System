from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Book


app = FastAPI(
    title="Library Management API",
    description="Backend API for Library Management System",
    version="1.0"
)


# Database dependency

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()



# Endpoint 1
# Get all books

@app.get("/books")
def get_books(
    db: Session = Depends(get_db)
):

    books = db.query(Book).all()

    return [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author
        }
        for book in books
    ]



# Endpoint 2
# Search books

@app.get("/books/search")
def search_books(
    title: str = Query(
        None,
        description="Search book by title"
    ),
    db: Session = Depends(get_db)
):

    query = db.query(Book)


    if title:

        query = query.filter(
            Book.title.ilike(
                f"%{title}%"
            )
        )


    books = query.all()


    return [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author
        }
        for book in books
    ]
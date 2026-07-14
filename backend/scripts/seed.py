from backend.db.session import SessionLocal
from backend.models import Book, Member

db = SessionLocal()

if db.query(Book).count() == 0:

    books = [
        Book(title="Python Basics", author="John Smith"),
        Book(title="Learning SQL", author="Jane Doe"),
        Book(title="Docker Essentials", author="Mike Brown")
    ]

    members = [
        Member(name="Ali"),
        Member(name="Ahmed")
    ]

    db.add_all(books)
    db.add_all(members)

    db.commit()

print("Sample data inserted.")

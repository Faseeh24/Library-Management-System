from database import SessionLocal, engine, Base
from models import Book, Member, Loan


# Create tables if they do not exist
Base.metadata.create_all(bind=engine)


def add_book(db):
    title = input("Enter book title: ")
    author = input("Enter author name: ")

    book = Book(
        title=title,
        author=author
    )

    db.add(book)
    db.commit()

    print("Book added successfully!")


def view_books(db):
    books = db.query(Book).all()

    print("\n===== Available Books =====")

    if not books:
        print("No books found.")
        return

    for book in books:
        print(
            f"ID: {book.id} | "
            f"Title: {book.title} | "
            f"Author: {book.author}"
        )


def delete_book(db):
    book_id = input("Enter book ID to delete: ")

    book = db.query(Book).filter(
        Book.id == int(book_id)
    ).first()

    if book:
        db.delete(book)
        db.commit()
        print("Book deleted successfully!")

    else:
        print("Book not found.")


def add_member(db):
    name = input("Enter member name: ")

    member = Member(
        name=name
    )

    db.add(member)
    db.commit()

    print("Member added successfully!")


def view_members(db):
    members = db.query(Member).all()

    print("\n===== Members =====")

    if not members:
        print("No members found.")
        return

    for member in members:
        print(
            f"ID: {member.id} | "
            f"Name: {member.name}"
        )


def create_loan(db):

    book_id = int(input("Enter book ID: "))
    member_id = int(input("Enter member ID: "))

    loan = Loan(
        book_id=book_id,
        member_id=member_id
    )

    db.add(loan)
    db.commit()

    print("Book issued successfully!")


def view_loans(db):

    loans = db.query(Loan).all()

    print("\n===== Loans =====")

    if not loans:
        print("No loans found.")
        return

    for loan in loans:
        print(
            f"Loan ID: {loan.id} | "
            f"Book ID: {loan.book_id} | "
            f"Member ID: {loan.member_id}"
        )


def menu():

    db = SessionLocal()

    while True:

        print("\n===== Library Management System =====")
        print("1. Add Book")
        print("2. View Books")
        print("3. Delete Book")
        print("4. Add Member")
        print("5. View Members")
        print("6. Issue Book")
        print("7. View Loans")
        print("8. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            add_book(db)

        elif choice == "2":
            view_books(db)

        elif choice == "3":
            delete_book(db)

        elif choice == "4":
            add_member(db)

        elif choice == "5":
            view_members(db)

        elif choice == "6":
            create_loan(db)

        elif choice == "7":
            view_loans(db)

        elif choice == "8":
            print("Goodbye!")
            break

        else:
            print("Invalid choice.")

    db.close()


if __name__ == "__main__":
    menu()

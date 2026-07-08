import os
import time
import psycopg2


def get_connection():
    while True:
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "postgres"),
                database=os.getenv("DB_NAME", "librarydb"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "password"),
                port=os.getenv("DB_PORT", "5432"),
            )
            print("Connected to PostgreSQL!")
            return conn

        except psycopg2.OperationalError:
            print("Waiting for PostgreSQL...")
            time.sleep(2)


def create_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100),
            author VARCHAR(100)
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


def add_book():
    title = input("Enter book title: ")
    author = input("Enter author: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO books (title, author) VALUES (%s, %s)",
        (title, author)
    )

    conn.commit()
    cur.close()
    conn.close()

    print("Book added successfully!")


def view_books():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM books")
    books = cur.fetchall()

    print("\nLibrary Books")
    print("-" * 30)

    if not books:
        print("No books available.")
    else:
        for book in books:
            print(f"ID: {book[0]}")
            print(f"Title: {book[1]}")
            print(f"Author: {book[2]}")
            print("-" * 30)

    cur.close()
    conn.close()


def delete_book():
    book_id = input("Enter Book ID to delete: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM books WHERE id = %s", (book_id,))

    conn.commit()
    cur.close()
    conn.close()

    print("Book deleted successfully!")


def menu():
    create_table()

    while True:
        print("\n===== Library Management System =====")
        print("1. Add Book")
        print("2. View Books")
        print("3. Delete Book")
        print("4. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            add_book()

        elif choice == "2":
            view_books()

        elif choice == "3":
            delete_book()

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    menu()

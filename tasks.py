"""Celery tasks for the library management system."""

import csv
import logging
import os
from datetime import datetime

from celery_app import celery_app
from database import SessionLocal, Base, engine
from models import Book, Loan, Member


# Ensure the worker can access the same tables as the API process.
Base.metadata.create_all(bind=engine)

logger = logging.getLogger(__name__)
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")


@celery_app.task(name="tasks.generate_library_report")
def generate_library_report():
    db = SessionLocal()
    try:
        os.makedirs(REPORTS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(REPORTS_DIR, f"library_report_{timestamp}.csv")

        logger.info("Report generation started: %s", report_path)

        books = db.query(Book).all()
        members = db.query(Member).all()
        loans = db.query(Loan).all()

        with open(report_path, "w", newline="", encoding="utf-8") as report_file:
            writer = csv.writer(report_file)
            writer.writerow(["section", "id", "title_or_name", "author_or_book_id", "member_id"])

            for book in books:
                writer.writerow(["book", book.id, book.title, book.author, ""])

            for member in members:
                writer.writerow(["member", member.id, member.name, "", ""])

            for loan in loans:
                writer.writerow(["loan", loan.id, "", loan.book_id, loan.member_id])

        logger.info("Report generation finished: %s", report_path)
        return {"report_path": report_path}
    except Exception:
        logger.exception("Report generation failed")
        raise
    finally:
        db.close()

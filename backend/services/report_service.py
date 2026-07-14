import csv
import logging
import os
from datetime import datetime

from backend.core.config import REPORTS_DIR
from backend.db.session import SessionLocal
from backend import models

logger = logging.getLogger(__name__)


def generate_library_report() -> str:
    db = SessionLocal()
    try:
        os.makedirs(REPORTS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(REPORTS_DIR, f'library_report_{timestamp}.csv')

        logger.info('Report generation started: %s', report_path)

        books = db.query(models.Book).all()
        members = db.query(models.Member).all()
        loans = db.query(models.Loan).all()

        with open(report_path, 'w', newline='', encoding='utf-8') as report_file:
            writer = csv.writer(report_file)
            writer.writerow(['section', 'id', 'title_or_name', 'author_or_book_id', 'member_id'])

            for book in books:
                writer.writerow(['book', book.id, book.title, book.author, ''])

            for member in members:
                writer.writerow(['member', member.id, member.name, '', ''])

            for loan in loans:
                writer.writerow(['loan', loan.id, '', loan.book_id, loan.member_id])

        logger.info('Report generation finished: %s', report_path)
        return report_path
    except Exception:
        logger.exception('Report generation failed')
        raise
    finally:
        db.close()

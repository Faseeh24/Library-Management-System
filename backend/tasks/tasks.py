"""Celery tasks for the library management system."""

from backend.tasks.celery_app import celery_app

from backend.services.report_service import generate_library_report as generate_library_report_file


@celery_app.task(name='tasks.generate_library_report')
def generate_library_report():
    return {'report_path': generate_library_report_file()}

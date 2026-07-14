from fastapi import APIRouter, BackgroundTasks, status

from backend.tasks.tasks import generate_library_report

router = APIRouter(prefix='/reports', tags=['Reports'])


@router.post('/generate', status_code=status.HTTP_202_ACCEPTED)
def generate_report(background_tasks: BackgroundTasks):
    task = generate_library_report.delay()
    return {'message': 'Report generation queued', 'task_id': task.id}

from fastapi import APIRouter

from backend.routes.auth import router as auth_router
from backend.routes.books import router as books_router
from backend.routes.loans import router as loans_router
from backend.routes.members import router as members_router
from backend.routes.reports import router as reports_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(books_router)
api_router.include_router(loans_router)
api_router.include_router(members_router)
api_router.include_router(reports_router)

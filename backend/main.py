from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.router import api_router
from backend.core.config import FRONTEND_ORIGINS
from backend.db.session import Base, engine
from backend import models  # noqa: F401

app = FastAPI(
    title='Library Management API',
    description='Backend API for Library Management System',
    version='1.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

Base.metadata.create_all(bind=engine)
app.include_router(api_router)

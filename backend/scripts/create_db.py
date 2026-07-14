from backend.db.session import Base, engine
from backend import models

Base.metadata.create_all(bind=engine)

print("Database tables created.")

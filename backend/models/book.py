from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.db.session import Base


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    author = Column(String(100), nullable=False)

    loans = relationship('Loan', back_populates='book', cascade='all, delete-orphan')

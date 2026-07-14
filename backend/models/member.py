from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.db.session import Base


class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    loans = relationship('Loan', back_populates='member', cascade='all, delete-orphan')

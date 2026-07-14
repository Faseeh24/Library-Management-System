from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from backend.db.session import Base


class Loan(Base):
    __tablename__ = 'loans'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id', ondelete='CASCADE'))
    member_id = Column(Integer, ForeignKey('members.id', ondelete='CASCADE'))

    book = relationship('Book', back_populates='loans')
    member = relationship('Member', back_populates='loans')

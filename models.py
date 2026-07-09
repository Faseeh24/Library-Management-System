from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    author = Column(String(100), nullable=False)

    loans = relationship("Loan", back_populates="book", cascade="all, delete-orphan")


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    loans = relationship("Loan", back_populates="member", cascade="all, delete-orphan")


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True)

    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"))
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"))

    book = relationship("Book", back_populates="loans")
    member = relationship("Member", back_populates="loans")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="member")

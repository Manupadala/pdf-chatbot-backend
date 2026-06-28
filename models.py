from sqlalchemy import Column,Integer,String,Text
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(String(100))

    email = Column(
        String(100),
        unique=True
    )

    password = Column(String(255))

from sqlalchemy import Column, Integer, String, Text

class ChatHistory(Base):

    __tablename__ = "chat_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    user_email = Column(String(100), index=True)
    pdf_name = Column(
        String(255)
    )

    question = Column(
        Text
    )

    answer = Column(
        Text
    )

class PDFFile(Base):

    __tablename__ = "pdf_files"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    filename = Column(
        String(255)
    )

    user_email = Column(
        String(100),
        index=True
    )
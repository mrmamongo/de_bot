import enum

from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from doeba_bot.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    is_admin = Column(Boolean, default=False)
    documents = relationship("Doc", backref="users")


class DocStatus(enum.Enum):
    new = "new"
    in_progress = "in_progress"
    done = "done"


class Doc(Base):
    __tablename__ = "docs"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    status = Column(Enum(DocStatus), default="new")
    url = Column(String, unique=True)
    created_at = Column(DateTime, server_default="now()")
    edited_at = Column(DateTime, server_default="now()")
    author_id = Column(Integer, ForeignKey("users.id"))
    comments = relationship("Comment", backref="docs")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    text = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))
    doc_id = Column(Integer, ForeignKey("docs.id"))

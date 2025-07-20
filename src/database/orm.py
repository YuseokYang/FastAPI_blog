from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String(30), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    email: str | None = Column(String(255), nullable=True)
    admin = Column(Boolean, default=False)
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete")

    @classmethod
    def create(cls, username: str, hashed_password: str, email: str | None):
        return cls(
            username=username,
            hashed_password=hashed_password,
            email=email
        )


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default = datetime.now(timezone.utc))
    is_pinned = Column(Boolean, default=False)
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete")

    @classmethod
    def create(cls, post_data, user_id):
        return cls(
            title=post_data.title,
            content=post_data.content,
            user_id=user_id
        )

    def pinned(self):
        self.is_pinned=True

    def unpinned(self):
        self.is_pinned=False


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    post = relationship("Post", back_populates="comments")
    user = relationship("User", back_populates="comments")

    @classmethod
    def create(cls, post_id, content, user_id):
        return cls(
            post_id=post_id,
            content=content,
            user_id=user_id,
        )
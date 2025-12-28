from typing import Annotated, Optional, List
from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship


class Author(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    surname: str = Field(index=True)
    birth_date: date | None = Field(default=None)
    
    books: List["Book"] = Relationship(back_populates="author")


class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str | None = Field(default=None)
    genre: str | None = Field(default=None, index=True)
    author_id: int | None = Field(default=None, foreign_key="author.id")
    
    # Relationships
    author: Author | None = Relationship(back_populates="books")
    comments: List["Comment"] = Relationship(back_populates="book")


class Comment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content: str
    book_id: int | None = Field(default=None, foreign_key="book.id")
    
    # Relationship to book
    book: Book | None = Relationship(back_populates="comments")

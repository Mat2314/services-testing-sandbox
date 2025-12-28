from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, create_engine, Session, select
from typing import List
import os
from datetime import date
from contextlib import asynccontextmanager

from models import Author, Book, Comment

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/mydb")
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI(
    title="Library API", 
    description="API for managing authors, books, and comments",
)

@app.get("/")
async def root():
    return {"message": "Library API - Manage authors, books, and comments"}

# Author endpoints
@app.post("/authors/", response_model=Author)
def create_author(author: Author, session: Session = Depends(get_session)):
    session.add(author)
    session.commit()
    session.refresh(author)
    return author

@app.get("/authors/", response_model=List[Author])
def read_authors(session: Session = Depends(get_session)):
    authors = session.exec(select(Author)).all()
    return authors

@app.get("/authors/{author_id}", response_model=Author)
def read_author(author_id: int, session: Session = Depends(get_session)):
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author

# Book endpoints
@app.post("/books/", response_model=Book)
def create_book(book: Book, session: Session = Depends(get_session)):
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@app.get("/books/", response_model=List[Book])
def read_books(session: Session = Depends(get_session)):
    books = session.exec(select(Book)).all()
    return books

@app.get("/books/{book_id}", response_model=Book)
def read_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# Comment endpoints
@app.post("/comments/", response_model=Comment)
def create_comment(comment: Comment, session: Session = Depends(get_session)):
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment

@app.get("/comments/", response_model=List[Comment])
def read_comments(session: Session = Depends(get_session)):
    comments = session.exec(select(Comment)).all()
    return comments

@app.get("/books/{book_id}/comments/", response_model=List[Comment])
def read_book_comments(book_id: int, session: Session = Depends(get_session)):
    comments = session.exec(select(Comment).where(Comment.book_id == book_id)).all()
    return comments
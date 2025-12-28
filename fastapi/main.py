from fastapi import FastAPI, Depends, HTTPException, Request, Response
from sqlmodel import SQLModel, create_engine, Session, select
from typing import List
import os, time

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

from models import Author, Book, Comment

# ----------------------
# Metrics definitions
# ----------------------

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
)

IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "In-progress HTTP requests",
)


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

# ----------------------
# Middleware
# ----------------------

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    # 1️⃣ Skip metrics endpoint (avoid self-scraping)
    if request.url.path == "/metrics":
        return await call_next(request)

    method = request.method

    IN_PROGRESS.inc()
    start_time = time.time()

    try:
        # 2️⃣ Execute request FIRST (route is resolved here)
        response = await call_next(request)
        status = response.status_code
        return response

    finally:
        duration = time.time() - start_time
        IN_PROGRESS.dec()

        # 3️⃣ Get normalized route path AFTER call_next
        route = request.scope.get("route")
        path = route.path if route else "unknown"

        # 4️⃣ Record metrics
        REQUEST_COUNT.labels(
            method=method,
            path=path,
            status=status,
        ).inc()

        REQUEST_LATENCY.labels(
            method=method,
            path=path,
        ).observe(duration)

# ----------------------
# Metrics endpoint
# ----------------------

@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
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
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, mentors, courses, search

load_dotenv()

app = FastAPI(
    title="Peer Mentoring System",
    description="Akran Mentörlük Sistemi API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:5173")
    ],
    allow_credentials=False,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS"
    ],
    allow_headers=[
        "Accept",
        "Content-Type",
        "Authorization"
    ],
)


app.include_router(auth.router)
app.include_router(mentors.router)
app.include_router(courses.router)
app.include_router(search.router)


@app.get("/")
def home():
    return {"message": "Peer Mentoring System API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
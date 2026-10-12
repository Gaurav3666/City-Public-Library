
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.database import initialize_database
from app.routers.books import router as books_router
from app.routers.members import router as members_router
from app.routers.loans import router as loans_router
from app.routers.fines import router as fines_router
from app.routers.reports import router as reports_router
from app.routers.partners import router as partners_router
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

SESSION_SECRET = os.getenv("SESSION_SECRET")


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database(seed=False)
    yield


app = FastAPI(
    title="City Public Library API",
    description="Backend API for a three-branch public library",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not SESSION_SECRET:
    raise RuntimeError(
        "SESSION_SECRET is missing. Configure backend/.env."
    )

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="library_staff_session",
    max_age=1800,
    same_site="lax",
    https_only=False,  # Local development only; use True with production HTTPS.
)


@app.get("/")
def home():
    return {"message": "City Public Library API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(books_router)
app.include_router(members_router)
app.include_router(loans_router)
app.include_router(fines_router)
app.include_router(reports_router)
app.include_router(partners_router)

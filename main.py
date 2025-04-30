from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import models
from database import engine, get_db
from src.routers import auth, users, tasks

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Task Manager API"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
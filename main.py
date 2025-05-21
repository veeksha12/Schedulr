from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import date

from db import create_db_and_tables
from path import auth, progress, courses, exams, planner, todo, sonar
from models import Task

app = FastAPI(
    title="Study Planner API",
    description="Helps users track their study goals, exams, and grades intelligently using Perplexity's Sonar API.",
    version="1.0.0"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with prefix /api for all
app.include_router(auth.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(courses.router, prefix="/api")
app.include_router(exams.router, prefix="/api")
app.include_router(planner.router, prefix="/api")
app.include_router(todo.router, prefix="/api")
app.include_router(sonar.router, prefix="/api")

# Startup event to create DB tables
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def root():
    return {"message": "Study Planner API is live."}

# In-memory task storage
tasks_db: List[Task] = []
task_counter = 1

@app.post("/tasks/")
def create_task(description: str):
    global task_counter
    task = Task(id=task_counter, date=str(date.today()), description=description, completed=False)
    tasks_db.append(task)
    task_counter += 1
    return task

@app.get("/tasks/today", response_model=List[Task])
def get_today_tasks():
    today = str(date.today())
    return [task for task in tasks_db if task.date == today]

@app.get("/tasks/history", response_model=List[Task])
def get_task_history():
    return tasks_db

@app.put("/tasks/{task_id}")
def update_task_status(task_id: int, completed: bool):
    for task in tasks_db:
        if task.id == task_id:
            task.completed = completed
            return task
    raise HTTPException(status_code=404, detail="Task not found")

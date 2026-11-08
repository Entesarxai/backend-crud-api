import sqlite3
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel 

app = FastAPI()

conn = sqlite3.connect("tasks.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS tasks(
id INTEGER PRIMARY KEY,
title TEXT,
done INTEGER
)
""")

conn.commit()

count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]

if count == 0:
    conn.execute(
        "INSERT INTO tasks (title, done) VALUES (?,?)",
        ("Learn FastAPI", 0)
    )
    conn.execute(
        "INSERT INTO tasks (title, done) VALUES (?,?)",
        ("Build CRU D API", 0)
    )
    conn.execute(
        "INSERT INTO tasks (title, done) VALUES (?,?)",
        ("Test the API", 1)
    )
    conn.commit()

class TaskCreate(BaseModel):
    title: str | None = None 

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

tasks = [{"id": 1, "title": "Learn FastAPI", "done": False},
         {"id": 2, "title": "Build CRUD API", "done": False},
          {"id": 3, "title": "Test the API", "done": True} ]

@app.get("/", summary="Show API information")
def hello():
    return {"name": "Task API",
            "version": "1.0",
            "endpoints": ["/tasks"]}

@app.get("/health", summary="Check API health")
def status():
    return {"status": "ok"}

@app.get("/tasks", summary="List all tasks")
def get_tasks():

    db = sqlite3.connect("tasks.db")

    rows = db.execute(
        "SELECT id, title, done FROM tasks"
    ).fetchall()

    db.close()

    return [
        {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2])
        } 
        for row in rows
    ]

@app.get("/tasks/{id}", summary="Get one task")
def get_tasks_id(id: int):
    db = sqlite3.connect("tasks.db")

    row = db.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (id,)
    ).fetchone()
    db.close()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {id} not found"}
        )
    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2])
    }

@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(task: TaskCreate):
    if not task.title:
        return JSONResponse(
            status_code = 400,
            content={"error": "Title is required"}
        )
    
    new_id = max(t["id"] for t in tasks) + 1

    new_task = {
        "id": new_id,
        "title": task.title,
        "done": False
    }

    tasks.append(new_task)

    return new_task

@app.put("/tasks/{id}", summary="Update a task")
def update_task(id: int, update: TaskUpdate):

    if update.title is None and update.done is None:
        return JSONResponse(
            status_code=400,
            content={"error": "At least one field is required"}
        )
    
    for task in tasks:
        if task["id"] == id:
            if update.title is not None:
                task["title"] = update.title

            if update.done is not None:
                task["done"] = update.done

            return task
        
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {id} not found"}
    )

@app.delete("/tasks/{id}", summary="Delete a task")
def delete_task(id: int):
    for task in tasks:
        if task["id"] == id:
            tasks.remove(task)
            return Response(status_code=204)

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {id} not found"}
    )
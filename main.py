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
    conn.close()

class TaskCreate(BaseModel):
    title: str | None = None 

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

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
    
    db = sqlite3.connect("tasks.db")
    cursor = db.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task.title, 0)
    )

    new_id = cursor.lastrowid

    db.commit()
    db.close()

    return {
        "id": new_id,
        "title": task.title,
        "done": False
    }

@app.put("/tasks/{id}", summary="Update a task")
def update_task(id: int, update: TaskUpdate):

    if update.title is None and update.done is None:
        return JSONResponse(
            status_code=400,
            content={"error": "At least one field is required"}
        )
    
    db = sqlite3.connect("tasks.db")

    row = db.execute(
    "SELECT id, title, done FROM tasks WHERE id = ?", (id,)
    ).fetchone()

    if row is None:
       db.close()
       return JSONResponse(
        status_code=404,
        content={"error": f"Task {id} not found"}
       )

    current_title = row[1]
    current_done = bool(row[2])

    new_title = update.title if update.title is not None else current_title
    new_done = update.done if update .done is not None else current_done

    db.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?", (new_title, int(new_done), id))

    db.commit()
    db.close() 

    return {
        "id": id,
        "title": new_title,
        "done": new_done
    }

@app.delete("/tasks/{id}", summary="Delete a task")
def delete_task(id: int):

    db = sqlite3.connect("tasks.db")

    cursor = db.execute(
        "DELETE FROM tasks WHERE id = ?", (id,)
    )

    if cursor.rowcount == 0:
        db.close()

        return JSONResponse(
            status_code=404,
            content={"error": f"Task {id} not found"}
        )

    db.commit()
    db.close()

    return Response(status_code=204)
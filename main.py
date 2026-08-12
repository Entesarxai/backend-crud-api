from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel 

app = FastAPI()

class TaskCreate(BaseModel):
    title: str | None = None 

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

tasks = [{"id": 1, "title": "Learn FastAPI", "done": False},
         {"id": 2, "title": "Build CRUD API", "done": False},
          {"id": 3, "title": "Test the API", "done": True} ]

@app.get("/")
def hello():
    return {"name": "Task API",
            "version": "1.0",
            "endpoints": ["/tasks"]}

@app.get("/health")
def status():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{id}")
def get_tasks_id(id: int):
    for task in tasks:
        if task["id"]==id:
            return task
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {id} not found"}
    )

@app.post("/tasks", status_code=201)
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

@app.put("/tasks/{id}")
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

@app.delete("/tasks/{id}")
def delete_task(id: int):
    for task in tasks:
        if task["id"] == id:
            tasks.remove(task)
            return Response(status_code=204)

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {id} not found"}
    )
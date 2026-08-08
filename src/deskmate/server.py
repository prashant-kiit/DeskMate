import uvicorn
from fastapi import FastAPI

from deskmate.api import health, projects, tasks

app = FastAPI(root_path="/api")

app.include_router(health.router)
app.include_router(projects.router)
app.include_router(tasks.router)

def main():
    uvicorn.run("deskmate.server:app", host="0.0.0.0", port=8080, reload=True)
import uvicorn
from fastapi import FastAPI

from deskmate.api import health

app = FastAPI(root_path="/api")

app.include_router(health.router)

def main():
    uvicorn.run("deskmate:app", host="0.0.0.0", port=8080, reload=True)

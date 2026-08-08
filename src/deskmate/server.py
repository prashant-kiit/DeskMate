import uvicorn
from dotenv.main import load_dotenv
from fastapi import FastAPI

load_dotenv()

from deskmate.api import health, projects  # noqa: E402

app = FastAPI(root_path="/api")

app.include_router(health.router)
app.include_router(projects.router)

def main():
    uvicorn.run("deskmate.server:app", host="0.0.0.0", port=8080, reload=True)
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def get_health():
    return "ok"

def main():
    uvicorn.run("deskmate:app", host="0.0.0.0", port=8080, reload=True)

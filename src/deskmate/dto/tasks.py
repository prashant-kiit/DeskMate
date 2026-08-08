from pydantic import BaseModel


class TaskCreateRequest(BaseModel):
    name: str
    desc: str | None = None
    project_id : int

class TaskCreateResponse(BaseModel):
    id: int
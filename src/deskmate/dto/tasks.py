from datetime import datetime

from pydantic import BaseModel


class TaskOneFetchResponse(BaseModel):
    id: int
    name: str
    desc: str | None
    owner: str
    created_at: datetime
    updated_at: datetime
    project_id: int

class TaskCreateRequest(BaseModel):
    name: str
    desc: str | None = None
    project_id : int

class TaskCreateResponse(BaseModel):
    id: int
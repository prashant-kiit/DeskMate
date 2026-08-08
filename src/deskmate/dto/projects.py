from datetime import datetime

from pydantic import BaseModel


class ProjectFetchResponse(BaseModel):
    id:int
    name: str
    desc: str | None
    owner: str
    created_at: datetime
    updated_at: datetime

class ProjectCreateRequest(BaseModel):
    name: str
    desc: str | None = None

class ProjectCreateResponse(BaseModel):
    id: int
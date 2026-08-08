from pydantic import BaseModel


class ProjectCreateRequest(BaseModel):
    name: str
    desc: str | None = None

class ProjectCreateResponse(BaseModel):
    id: int
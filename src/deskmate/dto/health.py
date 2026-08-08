from enum import StrEnum

from pydantic import BaseModel


class HealthOutput(StrEnum):
    LIVE = "live"
    READY = "ready"
    NOT_LIVE = "not_live"
    NOT_READY = "not_ready"



class HealthResponse(BaseModel):
    message: str # for users
    output: HealthOutput # for developers
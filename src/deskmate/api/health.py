
from fastapi import APIRouter, status

from deskmate.model.health import HealthOutput, HealthResponse

router = APIRouter(prefix="/health", tags=["health"])

@router.get("", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def get_health() -> HealthResponse:
    return HealthResponse(message="application is up and running", output=HealthOutput.LIVE)
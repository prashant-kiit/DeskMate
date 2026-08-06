
from fastapi import APIRouter, status

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=None, status_code=status.HTTP_201_CREATED)
def create_project():
    return 
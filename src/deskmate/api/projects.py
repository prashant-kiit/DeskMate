
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from deskmate.dao.projects import Project
from deskmate.db import get_db

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=None, status_code=status.HTTP_201_CREATED)
async def create_project(db: AsyncSession = Depends(get_db)):
    project = Project(
        name="Test-0",
        owner="User-Test-0" 
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    return project

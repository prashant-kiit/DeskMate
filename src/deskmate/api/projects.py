
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from deskmate.dao.projects import Project
from deskmate.db import get_db
from deskmate.dto.projects import ProjectCreateRequest, ProjectCreateResponse

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=ProjectCreateResponse)
async def create_project(new_project: ProjectCreateRequest, db: AsyncSession = Depends(get_db)):
    project = Project(
        name=new_project.name,
        desc=new_project.desc,
        owner= "Prashant"
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    return project

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from deskmate.dao.projects import Project
from deskmate.dao.tasks import Task
from deskmate.db import get_db
from deskmate.dto.projects import (
    ProjectAllFetchResponse,
    ProjectCreateRequest,
    ProjectCreateResponse,
    ProjectOneFetchResponse,
)
from deskmate.dto.tasks import TaskAllFetchResponse

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("", response_model=list[ProjectAllFetchResponse])
async def get_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project.id, Project.name))
    
    projects = result.all()

    return projects

@router.get("/{project_id}", response_model=ProjectOneFetchResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id==project_id))
    
    project = result.scalars().one()

    return project

@router.get("/{project_id}/tasks", response_model=list[TaskAllFetchResponse])
async def get_tasks_by_project(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task.id, Task.name).where(Task.id==project_id))
    
    project = result.all()

    return project

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

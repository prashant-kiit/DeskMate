
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from deskmate.dao.tasks import Task
from deskmate.db import get_db
from deskmate.dto.tasks import TaskCreateRequest, TaskCreateResponse, TaskOneFetchResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/{task_id}", response_model=TaskOneFetchResponse)
async def get_project(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id==task_id))
    
    project = result.scalars().one()

    return project

@router.post("", response_model=TaskCreateResponse)
async def create_task(new_task: TaskCreateRequest, db: AsyncSession = Depends(get_db)):
    task = Task(
        name=new_task.name,
        desc=new_task.desc,
        owner= "Prashant",
        project_id = new_task.project_id
    )
    
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    return task

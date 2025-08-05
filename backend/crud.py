from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from database import TaskModel
from datetime import datetime
import uuid
from enum import Enum

# Enum для статусов задач 
class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

# Pydantic модели 
from pydantic import BaseModel
from typing import Optional

class TaskBase(BaseModel):
    title: str
    description: str

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None

class Task(TaskBase):
    id: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

# CRUD операции для задач

async def create_task(db: AsyncSession, task: TaskCreate) -> Task:
    """Создание новой задачи"""
    db_task = TaskModel(
        id=str(uuid.uuid4()),
        title=task.title,
        description=task.description,
        status=TaskStatus.TODO,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    
    # Конвертируем в Pydantic модель
    return Task(
        id=db_task.id,
        title=db_task.title,
        description=db_task.description,
        status=db_task.status,
        created_at=db_task.created_at,
        updated_at=db_task.updated_at
    )

async def get_tasks(db: AsyncSession) -> list[Task]:
    """Получение всех задач"""
    result = await db.execute(select(TaskModel))
    db_tasks = result.scalars().all()
    
    return [
        Task(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        for task in db_tasks
    ]

async def get_task(db: AsyncSession, task_id: str) -> Task | None:
    """Получение задачи по ID"""
    result = await db.execute(select(TaskModel).where(TaskModel.id == task_id))
    db_task = result.scalar_one_or_none()
    
    if db_task is None:
        return None
    
    return Task(
        id=db_task.id,
        title=db_task.title,
        description=db_task.description,
        status=db_task.status,
        created_at=db_task.created_at,
        updated_at=db_task.updated_at
    )

async def update_task(db: AsyncSession, task_id: str, task_update: TaskUpdate) -> Task | None:
    """Обновление задачи"""
    # Сначала получаем задачу
    result = await db.execute(select(TaskModel).where(TaskModel.id == task_id))
    db_task = result.scalar_one_or_none()
    
    if db_task is None:
        return None
    
    # Обновляем поля
    update_data = task_update.model_dump(exclude_unset=True)
    update_data['updated_at'] = datetime.utcnow()
    
    await db.execute(
        update(TaskModel)
        .where(TaskModel.id == task_id)
        .values(**update_data)
    )
    await db.commit()
    
    # Получаем обновленную задачу
    result = await db.execute(select(TaskModel).where(TaskModel.id == task_id))
    db_task = result.scalar_one()
    
    return Task(
        id=db_task.id,
        title=db_task.title,
        description=db_task.description,
        status=db_task.status,
        created_at=db_task.created_at,
        updated_at=db_task.updated_at
    )

async def delete_task(db: AsyncSession, task_id: str) -> bool:
    """Удаление задачи"""
    result = await db.execute(delete(TaskModel).where(TaskModel.id == task_id))
    await db.commit()
    return result.rowcount > 0 
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import json
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session, create_tables
from crud import create_task as crud_create_task, get_tasks as crud_get_tasks, get_task as crud_get_task, update_task as crud_update_task, delete_task as crud_delete_task

app = FastAPI(
    title="Kanban Board API",
    description="API для канбан-доски с поддержкой WebSocket синхронизации в реальном времени",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enum для статусов задач
class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

# Модели данных
class TaskBase(BaseModel):
    title: str = Field(..., description="Название задачи", min_length=1, max_length=200)
    description: str = Field(..., description="Описание задачи", min_length=1, max_length=1000)

class TaskCreate(TaskBase):
    """Модель для создания новой задачи"""
    pass

class Task(TaskBase):
    """Модель задачи с полной информацией"""
    id: str = Field(..., description="Уникальный идентификатор задачи")
    status: TaskStatus = Field(..., description="Статус задачи")
    created_at: datetime = Field(..., description="Дата и время создания")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

class TaskUpdate(BaseModel):
    """Модель для обновления задачи (все поля опциональны)"""
    title: Optional[str] = Field(None, description="Название задачи", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Описание задачи", min_length=1, max_length=1000)
    status: Optional[TaskStatus] = Field(None, description="Статус задачи")

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.active_connections.remove(connection)

manager = ConnectionManager()

async def broadcast_task_update():
    """Отправляет обновление всем подключенным клиентам"""
    db = await get_session()
    tasks = await crud_get_tasks(db)
    asyncio.create_task(manager.broadcast(json.dumps({
        "type": "tasks_update",
        "tasks": [task.model_dump(mode='json') for task in tasks]
    })))

# REST API endpoints
@app.get("/", tags=["Info"])
async def root():
    """
    Корневой эндпоинт API
    
    Возвращает информацию о API
    """
    return {
        "message": "Kanban Board API",
        "version": "1.0.0",
        "docs": "/docs",
        "websocket": "/ws"
    }

@app.get("/tasks", response_model=List[Task], tags=["Tasks"])
async def get_tasks(db: AsyncSession = Depends(get_session)):
    """
    Получить все задачи
    
    Возвращает список всех задач с их статусами
    """
    return await crud_get_tasks(db)

@app.post("/tasks", response_model=Task, tags=["Tasks"])
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_session)):
    """
    Создать новую задачу
    
    Создает новую задачу со статусом "todo" и отправляет уведомление через WebSocket
    """
    new_task = await crud_create_task(db, task)
    
    # Отправляем обновление через WebSocket
    await manager.broadcast(json.dumps({
        "type": "task_created",
        "task": new_task.model_dump(mode='json')
    }))
    
    return new_task

@app.get("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def get_task(task_id: str, db: AsyncSession = Depends(get_session)):
    """
    Получить задачу по ID
    
    Возвращает задачу по её уникальному идентификатору
    """
    task = await crud_get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def update_task(task_id: str, task_update: TaskUpdate, db: AsyncSession = Depends(get_session)):
    """
    Обновить задачу
    
    Обновляет задачу по ID. Можно изменить title, description или status.
    Отправляет уведомление через WebSocket при успешном обновлении.
    """
    updated_task = await crud_update_task(db, task_id, task_update)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Отправляем обновление через WebSocket
    await manager.broadcast(json.dumps({
        "type": "task_updated",
        "task": updated_task.model_dump(mode='json')
    }))
    
    return updated_task

@app.delete("/tasks/{task_id}", tags=["Tasks"])
async def delete_task(task_id: str, db: AsyncSession = Depends(get_session)):
    """
    Удалить задачу
    
    Удаляет задачу по ID и отправляет уведомление через WebSocket
    """
    success = await crud_delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Отправляем обновление через WebSocket
    await manager.broadcast(json.dumps({
        "type": "task_deleted",
        "task_id": task_id
    }))
    
    return {"message": "Task deleted successfully"}

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket соединение для real-time синхронизации
    
    При подключении отправляет текущее состояние всех задач.
    Поддерживает ping/pong для проверки соединения.
    """
    await manager.connect(websocket)
    try:
        # Отправляем текущее состояние при подключении
        db = await get_session()
        tasks = await crud_get_tasks(db)
        await websocket.send_text(json.dumps({
            "type": "initial_state",
            "tasks": [task.model_dump(mode='json') for task in tasks]
        }))
        
        while True:
            # Ожидаем сообщения от клиента
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Обрабатываем сообщения от клиента
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    import asyncio
    
    # Создаем таблицы при запуске
    async def init_db():
        await create_tables()
        print("Database initialized successfully!")
    
    # Запускаем инициализацию БД
    asyncio.run(init_db())
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 
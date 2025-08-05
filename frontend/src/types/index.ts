export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  created_at: string;
  updated_at: string;
}

export enum TaskStatus {
  TODO = 'todo',
  IN_PROGRESS = 'in_progress',
  DONE = 'done'
}

export interface CreateTaskRequest {
  title: string;
  description: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  status?: TaskStatus;
}

export interface WebSocketMessage {
  type: 'initial_state' | 'task_created' | 'task_updated' | 'task_deleted' | 'tasks_update' | 'ping' | 'pong';
  tasks?: Task[];
  task?: Task;
  task_id?: string;
}

export interface Column {
  id: TaskStatus;
  title: string;
  tasks: Task[];
} 
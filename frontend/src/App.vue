<template>
  <div id="app">
    <div class="connection-status" :class="{ connected: isConnected, disconnected: !isConnected }">
      {{ isConnected ? 'Connected' : 'Disconnected' }}
    </div>
    
    <div class="kanban-board">
      <KanbanColumn
        v-for="column in columns"
        :key="column.id"
        :column="column"
        :all-tasks="tasks"
        @task-moved="handleTaskMoved"
        @task-deleted="handleTaskDeleted"
        @task-created="handleTaskCreated"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { Task, TaskStatus, WebSocketMessage } from './types';
import { apiService } from './services/api';
import KanbanColumn from './components/KanbanColumn.vue';

const tasks = ref<Task[]>([]);
const isConnected = ref(false);

// Определяем колонки
const columns = computed(() => [
  {
    id: TaskStatus.TODO,
    title: 'To Do',
    tasks: tasks.value.filter(task => task.status === TaskStatus.TODO)
  },
  {
    id: TaskStatus.IN_PROGRESS,
    title: 'In Progress',
    tasks: tasks.value.filter(task => task.status === TaskStatus.IN_PROGRESS)
  },
  {
    id: TaskStatus.DONE,
    title: 'Done',
    tasks: tasks.value.filter(task => task.status === TaskStatus.DONE)
  }
]);

// Обработчики событий
const handleTaskMoved = async (taskId: string, newStatus: TaskStatus) => {
  console.log(`App: Moving task ${taskId} to status ${newStatus}`);
  console.log('Current tasks before update:', tasks.value);
  
  try {
    const updatedTask = await apiService.updateTask(taskId, { status: newStatus });
    console.log('Task updated successfully:', updatedTask);
    console.log('Current tasks after update:', tasks.value);
  } catch (error) {
    console.error('Failed to move task:', error);
  }
};

const handleTaskDeleted = async (taskId: string) => {
  try {
    await apiService.deleteTask(taskId);
  } catch (error) {
    console.error('Failed to delete task:', error);
  }
};

const handleTaskCreated = async (taskData: { title: string; description: string }) => {
  try {
    await apiService.createTask(taskData);
  } catch (error) {
    console.error('Failed to create task:', error);
  }
};

// Обработчик WebSocket сообщений
const handleWebSocketMessage = (message: WebSocketMessage) => {
  console.log('WebSocket message received:', message);
  
  switch (message.type) {
    case 'initial_state':
      if (message.tasks) {
        console.log('Setting initial state with tasks:', message.tasks);
        tasks.value = message.tasks;
      }
      break;
    case 'task_created':
      if (message.task) {
        console.log('Task created:', message.task);
        const existingIndex = tasks.value.findIndex(t => t.id === message.task!.id);
        if (existingIndex === -1) {
          tasks.value.push(message.task);
        }
      }
      break;
    case 'task_updated':
      if (message.task) {
        console.log('Task updated:', message.task);
        const index = tasks.value.findIndex(t => t.id === message.task!.id);
        if (index !== -1) {
          tasks.value[index] = message.task;
        } else {
          console.warn('Task not found for update:', message.task.id);
        }
      }
      break;
    case 'task_deleted':
      if (message.task_id) {
        console.log('Task deleted:', message.task_id);
        tasks.value = tasks.value.filter(t => t.id !== message.task_id);
      }
      break;
    case 'tasks_update':
      if (message.tasks) {
        console.log('Tasks updated:', message.tasks);
        tasks.value = message.tasks;
      }
      break;
    default:
      console.log('Unknown message type:', message.type);
  }
  
  console.log('Tasks after processing message:', tasks.value);
};

// Обработчик изменения статуса подключения
const handleConnectionStatusChange = (connected: boolean) => {
  isConnected.value = connected;
};

// Загрузка начальных данных
const loadInitialData = async () => {
  try {
    tasks.value = await apiService.getTasks();
  } catch (error) {
    console.error('Failed to load initial data:', error);
  }
};

// Жизненный цикл
onMounted(async () => {
  await loadInitialData();
  apiService.connectWebSocket(handleWebSocketMessage, handleConnectionStatusChange);
});

onUnmounted(() => {
  apiService.disconnectWebSocket();
});
</script> 
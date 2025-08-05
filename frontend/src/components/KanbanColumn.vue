<template>
  <div 
    class="column" 
    :class="[columnClass, { 'drag-over': isDragOver }]"
    @dragover="handleDragOver"
    @drop="handleDrop"
    @dragenter="handleDragEnter"
    @dragleave="handleDragLeave"
    @dragend="handleDragEnd"
  >
    <div class="column-header">
      <h2 class="column-title">{{ column.title }}</h2>
      <span class="column-count">{{ column.tasks.length }}</span>
    </div>
    
    <div class="task-list">
      <TaskCard
        v-for="task in column.tasks"
        :key="task.id"
        :task="task"
        @delete="handleDeleteTask"
        @dragstart="handleDragStart"
        @dragend="handleDragEnd"
      />
      
      <div 
        v-if="column.tasks.length === 0"
        class="drop-zone"
        :class="{ 'drag-over': isDragOver }"
      >
        Drop tasks here
      </div>
    </div>
    
    <AddTaskForm 
      v-if="column.id === 'todo'"
      @task-created="handleTaskCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { Task, TaskStatus } from '../types';
import TaskCard from './TaskCard.vue';
import AddTaskForm from './AddTaskForm.vue';

interface Props {
  column: {
    id: TaskStatus;
    title: string;
    tasks: Task[];
  };
  allTasks: Task[]; // Добавляем все задачи
}

const props = defineProps<Props>();
const emit = defineEmits<{
  taskMoved: [taskId: string, newStatus: TaskStatus];
  taskDeleted: [taskId: string];
  taskCreated: [taskData: { title: string; description: string }];
}>();

const isDragOver = ref(false);
const draggedTask = ref<Task | null>(null);

// CSS класс для колонки
const columnClass = computed(() => {
  switch (props.column.id) {
    case TaskStatus.TODO:
      return 'todo';
    case TaskStatus.IN_PROGRESS:
      return 'in-progress';
    case TaskStatus.DONE:
      return 'done';
    default:
      return '';
  }
});

// Обработчики drag-and-drop
const handleDragStart = (task: Task) => {
  console.log('KanbanColumn: Drag start for task:', task.id);
  draggedTask.value = task;
  console.log('KanbanColumn: Set draggedTask to:', draggedTask.value);
};

const handleDragEnd = () => {
  console.log('KanbanColumn: Drag end, draggedTask before:', draggedTask.value);
  // НЕ очищаем draggedTask здесь, даем время для handleDrop
  isDragOver.value = false;
  // Очищаем draggedTask только если drop не произошел
  setTimeout(() => {
    if (draggedTask.value) {
      console.log('KanbanColumn: Clearing draggedTask in handleDragEnd');
      draggedTask.value = null;
    }
  }, 100);
};

const handleDragOver = (event: DragEvent) => {
  event.preventDefault();
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move';
  }
  console.log('KanbanColumn: Drag over column:', props.column.id);
};

const handleDragEnter = (event: DragEvent) => {
  event.preventDefault();
  isDragOver.value = true;
};

const handleDragLeave = (event: DragEvent) => {
  // Проверяем, что мы действительно покидаем колонку, а не переходим к дочернему элементу
  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
  const x = event.clientX;
  const y = event.clientY;
  
  if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
    isDragOver.value = false;
  }
};

const handleDrop = (event: DragEvent) => {
  event.preventDefault();
  isDragOver.value = false;
  
  console.log('KanbanColumn: Drop event triggered');
  console.log('draggedTask:', draggedTask.value);
  console.log('column.id:', props.column.id);
  
  // Сначала попробуем использовать draggedTask
  let taskToMove = draggedTask.value;
  
  // Если draggedTask null, попробуем получить из dataTransfer
  if (!taskToMove && event.dataTransfer) {
    const taskId = event.dataTransfer.getData('text/plain');
    console.log('Task ID from dataTransfer:', taskId);
    
    if (taskId) {
      // Найдем задачу во всех задачах
      taskToMove = props.allTasks.find(task => task.id === taskId);
      console.log('Found task in allTasks:', taskToMove);
    }
  }
  
  if (taskToMove && taskToMove.status !== props.column.id) {
    console.log(`Moving task ${taskToMove.id} from ${taskToMove.status} to ${props.column.id}`);
    emit('taskMoved', taskToMove.id, props.column.id);
  } else {
    console.log('No task to move or task already in this column');
  }
  
  // Очищаем draggedTask сразу
  draggedTask.value = null;
};

// Обработчики событий
const handleDeleteTask = (taskId: string) => {
  emit('taskDeleted', taskId);
};

const handleTaskCreated = (taskData: { title: string; description: string }) => {
  emit('taskCreated', taskData);
};
</script> 
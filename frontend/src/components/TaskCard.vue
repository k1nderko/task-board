<template>
  <div 
    class="task-card"
    :class="{ dragging: isDragging }"
    draggable="true"
    @dragstart="handleDragStart"
    @dragend="handleDragEnd"
  >
    <div class="task-title">{{ task.title }}</div>
    <div class="task-description">{{ task.description }}</div>
    <div class="task-actions">
      <button class="btn btn-delete" @click="handleDelete">
        Delete
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Task } from '../types';

interface Props {
  task: Task;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  delete: [taskId: string];
  dragstart: [task: Task];
  dragend: [];
}>();

const isDragging = ref(false);

const handleDragStart = (event: DragEvent) => {
  console.log('TaskCard: Drag start for task:', props.task.id);
  isDragging.value = true;
  if (event.dataTransfer) {
    event.dataTransfer.setData('text/plain', props.task.id);
    event.dataTransfer.effectAllowed = 'move';
  }
  emit('dragstart', props.task);
};

const handleDragEnd = () => {
  console.log('TaskCard: Drag end for task:', props.task.id);
  isDragging.value = false;
  emit('dragend');
};

const handleDelete = () => {
  if (confirm('Are you sure you want to delete this task?')) {
    emit('delete', props.task.id);
  }
};
</script> 
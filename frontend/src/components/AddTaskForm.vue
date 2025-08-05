<template>
  <div class="add-task-form">
    <h3>Add New Task</h3>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="title">Title</label>
        <input
          id="title"
          v-model="form.title"
          type="text"
          placeholder="Enter task title"
          required
        />
      </div>
      
      <div class="form-group">
        <label for="description">Description</label>
        <textarea
          id="description"
          v-model="form.description"
          placeholder="Enter task description"
          rows="3"
          required
        ></textarea>
      </div>
      
      <button 
        type="submit" 
        class="btn-add"
        :disabled="isSubmitting"
      >
        {{ isSubmitting ? 'Adding...' : 'Add Task' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const emit = defineEmits<{
  taskCreated: [taskData: { title: string; description: string }];
}>();

const form = ref({
  title: '',
  description: ''
});

const isSubmitting = ref(false);

const handleSubmit = async () => {
  if (!form.value.title.trim() || !form.value.description.trim()) {
    return;
  }
  
  isSubmitting.value = true;
  
  try {
    emit('taskCreated', {
      title: form.value.title.trim(),
      description: form.value.description.trim()
    });
    
    // Сбрасываем форму
    form.value.title = '';
    form.value.description = '';
  } catch (error) {
    console.error('Failed to create task:', error);
  } finally {
    isSubmitting.value = false;
  }
};
</script> 
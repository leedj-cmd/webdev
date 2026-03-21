<!-- filename: frontend/src/App.vue -->
<script setup>
import { ref } from 'vue'

const message = ref('Hello, Vue.js!')
</script>

<template>
  <div>
    <h1>{{ message }}</h1>
  </div>
</template>

<style scoped>
h1 {
  color: #42b883;
  text-align: center;
  margin-top: 100px;
}
</style>
<template>
  <div style="text-align:center; padding:3rem;">
    <h2>⛔ Unauthorized</h2>
    <p>You don't have permission to view this page.</p>
    <button @click="router.push('/dashboard')">Go Back</button>
  </div>
</template>
<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

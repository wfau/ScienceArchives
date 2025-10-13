<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import MenuBar from '@/components/MenuBar.vue'
</script>

<template>
  <header>
    <MenuBar />
  </header>
  <RouterView />
</template>

<style scoped>
</style>

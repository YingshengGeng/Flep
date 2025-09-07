<template>
  <div class="flex flex-nowrap items-center gap-2">
    <div class="size-2 rounded-full bg-[#0059E5]"></div>
    <p class="font-bold text-black">{{ title }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string }>()
</script>

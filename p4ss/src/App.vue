<template>
  <el-config-provider>
    <router-view />
  </el-config-provider>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
// import autofit from 'autofit.js'

onMounted(() => {
  /**
   * autofit.js 自适应
   * - el（可选）：渲染的元素，默认 'body'
   * - dw（可选）：设计稿的宽度，默认 1920
   * - dh（可选）：设计稿的高度，默认 1080
   * - resize（可选）：是否监听 resize 事件，默认 true
   * - ignore（可选)：忽略缩放的元素（该元素将反向缩放）
   * - transition（可选）：过渡时间，默认 0
   * - delay（可选）：延迟，默认 0
   */
  // autofit.init({ el: '#app', dw: 1920, dh: 1080 })
})
</script>

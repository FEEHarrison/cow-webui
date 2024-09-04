<template>
  <div v-if="error">
    <h2>发生错误</h2>
    <p>{{ error.message }}</p>
    <button @click="resetError">重试</button>
  </div>
  <slot v-else></slot>
</template>

<script>
import { ref, onErrorCaptured } from "vue";

export default {
  name: "ErrorBoundary",
  setup() {
    const error = ref(null);

    onErrorCaptured((err, instance, info) => {
      error.value = err;
      console.error("捕获到错误:", err, instance, info);
      return false; // 阻止错误继续传播
    });

    const resetError = () => {
      error.value = null;
    };

    return {
      error,
      resetError,
    };
  },
};
</script>

<style scoped>
/* 可以根据需要添加样式 */
</style>

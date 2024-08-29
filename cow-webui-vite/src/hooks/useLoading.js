import { ref } from 'vue';

/**
 * 用于处理加载状态的 hook
 * @returns {Object} loading 状态和包装函数 withLoading
 */
export function useLoading() {
  // 定义加载状态
  const loading = ref(false);

  /**
   * 包装函数，用于在请求时设置加载状态
   * @param {Function} fn 异步函数
   */
  const withLoading = async (fn) => {
    loading.value = true;
    try {
      await fn();  // 执行传入的异步函数
    } finally {
      loading.value = false;  // 请求完成后，恢复状态
    }
  };

  return {
    loading,
    withLoading,
  };
}

<template>
  <Header v-if="showHeader" />
  <router-view></router-view>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import Header from "@/components/Header.vue";

const route = useRoute();

const showHeader = computed(() => {
  return (
    route.path !== "/" && route.path !== "/login" && route.path !== "/register"
  );
});
</script>

<style scoped>
/* 全局样式 */
</style>

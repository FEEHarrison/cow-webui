<template>
  <div class="dashboard">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="机器人管理" name="bot-management">
        <BotManagement />
      </el-tab-pane>
      <el-tab-pane v-if="isAdmin" label="用户管理" name="user-management">
        <UserManagement />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import BotManagement from "@/views/BotManagement.vue";
import UserManagement from "@/views/UserManagement.vue";

const activeTab = ref("bot-management");
const isAdmin = ref(false);

onMounted(() => {
  isAdmin.value =
    localStorage.getItem("user") &&
    JSON.parse(localStorage.getItem("user")).role === "root";
});
</script>

<style scoped>
.dashboard {
  padding: 20px;
}
</style>

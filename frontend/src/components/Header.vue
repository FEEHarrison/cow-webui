<template>
  <el-header class="header">
    <div class="header-left">
      <h1 class="project-name">cow-webui</h1>
    </div>
    <!-- <el-button @click="handleClearUserData" type="danger"
      >清空用户数据</el-button
    > -->
    <div class="header-right">
      <el-dropdown trigger="hover" @command="handleCommand">
        <span class="el-dropdown-link">
          <el-avatar :src="userAvatar" class="user-avatar"></el-avatar>
          <span class="username">{{ username }}</span>
          <i class="el-icon-arrow-down el-icon--right"></i>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-header>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { logout } from "@/utils/request";
const router = useRouter();
const username = ref("");
const userAvatar = ref("https://via.placeholder.com/40"); // 默认头像

const fetchUserInfo = () => {
  const userString = localStorage.getItem("user");
  if (userString) {
    try {
      const userInfo = JSON.parse(userString);
      username.value = userInfo.username || "未知用户";
      // 如果有头像信息，可以在这里设置
      // userAvatar.value = userInfo.avatar || "https://via.placeholder.com/40";
    } catch (error) {
      console.error("解析用户信息失败:", error);
      username.value = "未知用户";
    }
  } else {
    username.value = "未登录";
  }
};

const handleCommand = async (command) => {
  try {
    await logout();
    ElMessage.success("已成功登出");
    router.push("/login");
  } catch (error) {
    ElMessage.error("登出失败");
  }
};

onMounted(() => {
  fetchUserInfo();
});
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background-color: #409eff;
  color: #fff;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
}
.el-dropdown-link {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
}
.project-name {
  margin: 0;
  font-size: 24px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-avatar {
  margin-right: 10px;
}

.username {
  margin-right: 10px;
}
</style>

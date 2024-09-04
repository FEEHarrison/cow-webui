<template>
  <el-card class="login-container">
    <template #header>
      <h2 class="card-header">登录</h2>
    </template>
    <el-form :model="form" @submit.prevent="onSubmit" label-position="top">
      <el-form-item label="用户名">
        <el-input
          v-model="form.username"
          placeholder="请输入用户名"
          @keyup.enter="onSubmit"
        ></el-input>
      </el-form-item>
      <el-form-item label="密码">
        <el-input
          type="password"
          v-model="form.password"
          placeholder="请输入密码"
          @keyup.enter="onSubmit"
          show-password
        ></el-input>
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          native-type="submit"
          :loading="loading"
          class="submit-btn"
        >
          登录
        </el-button>
      </el-form-item>
    </el-form>
    <div class="register-link">
      <span>没有账号？</span>
      <el-link type="primary" @click="goToRegister">立即注册</el-link>
    </div>
  </el-card>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { login } from "@/utils/request";

const form = ref({
  username: "",
  password: "",
});

const loading = ref(false);
const router = useRouter();

const onSubmit = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning("请输入用户名和密码");
    return;
  }

  loading.value = true;
  try {
    const response = await login(form.value);
    if (!response.error && response.success) {
      ElMessage.success("登录成功");
      router.push("/dashboard");
    }
  } catch (err) {
    ElMessage.error(err.message || "登录失败");
  } finally {
    loading.value = false;
  }
};

const goToRegister = () => {
  router.push("/register");
};
</script>

<style scoped>
.login-container {
  width: 400px;
  max-width: 400px;
  margin: 50px auto;
}

.card-header {
  text-align: center;
  font-weight: bold;
  height: 30px;
}

.submit-btn {
  width: 100%;
}

.register-link {
  margin-top: 20px;
  text-align: center;
}

.register-link span {
  margin-right: 5px;
}
</style>

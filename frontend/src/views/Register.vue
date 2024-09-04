<template>
  <el-card class="register-container">
    <template #header>
      <h2 class="card-header">注册</h2>
    </template>
    <el-form :model="form" @submit.prevent="onSubmit" label-position="top">
      <el-form-item label="用户名">
        <el-input v-model="form.username" placeholder="请输入用户名"></el-input>
      </el-form-item>
      <el-form-item label="密码">
        <el-input
          type="password"
          v-model="form.password"
          placeholder="请输入密码"
          show-password
        ></el-input>
      </el-form-item>
      <el-form-item label="确认密码">
        <el-input
          type="password"
          v-model="form.confirmPassword"
          placeholder="请再次输入密码"
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
          注册
        </el-button>
      </el-form-item>
    </el-form>
    <div class="login-link">
      <span>已有账号？</span>
      <el-link type="primary" @click="goToLogin">立即登录</el-link>
    </div>
  </el-card>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { register } from "@/api/user";

const form = ref({
  username: "",
  password: "",
  confirmPassword: "",
});

const loading = ref(false);
const router = useRouter();

const onSubmit = async () => {
  if (form.value.password !== form.value.confirmPassword) {
    ElMessage.error("两次输入的密码不一致");
    return;
  }

  loading.value = true;
  try {
    const response = await register({
      username: form.value.username,
      password: form.value.password,
    });
    if (response.success) {
      ElMessage.success("注册成功");
      router.push("/login");
    }
  } catch (err) {
    ElMessage.error(err.message || "注册失败");
  } finally {
    loading.value = false;
  }
};

const goToLogin = () => {
  router.push("/login");
};
</script>

<style scoped>
.register-container {
  width: 400px;
  max-width: 400px;
  margin: 50px auto;
}

.card-header {
  text-align: center;
  font-weight: bold;
}

.submit-btn {
  width: 100%;
}

.login-link {
  margin-top: 20px;
  text-align: center;
}

.login-link span {
  margin-right: 5px;
}
</style>

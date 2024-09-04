<template>
  <div class="register-container">
    <h2>注册</h2>
    <el-form :model="form" @submit.native.prevent="onSubmit">
      <el-form-item label="用户名">
        <el-input v-model="form.username"></el-input>
      </el-form-item>
      <el-form-item label="密码">
        <el-input type="password" v-model="form.password"></el-input>
      </el-form-item>
      <el-form-item label="确认密码">
        <el-input type="password" v-model="form.confirmPassword"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit" :loading="loading"
          >注册</el-button
        >
      </el-form-item>
    </el-form>
    <div class="login-link">
      <span>已有账号？</span>
      <el-link @click="goToLogin">立即登录</el-link>
    </div>
  </div>
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
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.login-link {
  margin-top: 20px;
  text-align: center;
}

.login-link span {
  margin-right: 5px;
}
</style>

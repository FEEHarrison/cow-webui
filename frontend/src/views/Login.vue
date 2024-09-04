<template>
  <div class="login-container">
    <h2>登录</h2>
    <el-form :model="form" @submit.native.prevent="onSubmit">
      <el-form-item label="用户名">
        <el-input v-model="form.username" @keyup.enter="onSubmit"></el-input>
      </el-form-item>
      <el-form-item label="密码">
        <el-input
          type="password"
          v-model="form.password"
          @keyup.enter="onSubmit"
        ></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" native-type="submit" :loading="loading"
          >登录</el-button
        >
      </el-form-item>
    </el-form>
    <div class="register-link">
      <span>没有账号？</span>
      <el-link @click="goToRegister">立即注册</el-link>
    </div>
  </div>
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
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.register-link {
  margin-top: 20px;
  text-align: center;
}

.register-link span {
  margin-right: 5px;
}
</style>

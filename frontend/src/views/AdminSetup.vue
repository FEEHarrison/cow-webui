<template>
  <div class="admin-setup">
    <h2>设置管理员密码</h2>
    <el-form :model="form" @submit.native.prevent="onSubmit">
      <el-form-item label="管理员密码">
        <el-input type="password" v-model="form.password"></el-input>
      </el-form-item>
      <el-form-item label="确认密码">
        <el-input type="password" v-model="form.confirmPassword"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit" :loading="loading"
          >设置密码</el-button
        >
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { setupAdmin, checkAdminSetup } from "@/api/user"; // 导入 setupAdmin 函数

const form = ref({
  password: "",
  confirmPassword: "",
});

const loading = ref(false);
const router = useRouter();

onMounted(async () => {
  try {
    const response = await checkAdminSetup();
    if (response.data.is_setup) {
      ElMessage.info("管理员已设置，正在跳转到登录页面");
      router.push("/login");
    }
  } catch (error) {
    ElMessage.error("检查管理员设置状态失败");
  }
});
const onSubmit = async () => {
  if (form.value.password !== form.value.confirmPassword) {
    ElMessage.error("两次输入的密码不一致");
    return;
  }

  loading.value = true;
  try {
    const response = await setupAdmin(form.value.password);
    if (response.success) {
      ElMessage.success(response.message || "管理员设置成功，请登录");
      router.push("/login");
    }
  } catch (error) {
    ElMessage.error(error.message || "设置管理员失败");
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.admin-setup {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>

<template>
  <el-card class="admin-setup">
    <template #header>
      <h2 class="card-title">设置管理员密码</h2>
    </template>
    <el-form :model="form" @submit.prevent="onSubmit" label-position="top">
      <el-form-item label="管理员密码">
        <el-input
          v-model="form.password"
          type="password"
          show-password
        ></el-input>
      </el-form-item>
      <el-form-item label="确认密码">
        <el-input
          v-model="form.confirmPassword"
          type="password"
          show-password
        ></el-input>
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          @click="onSubmit"
          :loading="loading"
          class="submit-button"
        >
          设置密码
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { setupAdmin, checkAdminSetup } from "@/api/user";

const form = ref({
  password: "",
  confirmPassword: "",
});

const loading = ref(false);
const router = useRouter();

onMounted(async () => {
  try {
    const { data } = await checkAdminSetup();
    if (data.is_setup) {
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
    const { success, message } = await setupAdmin(form.value.password);
    if (success) {
      ElMessage.success(message || "管理员设置成功，请登录");
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
  width: 400px;
  margin: 50px auto;
}

.card-title {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.submit-button {
  width: 100%;
}
</style>

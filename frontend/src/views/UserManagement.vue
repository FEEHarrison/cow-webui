<template>
  <div class="user-management-console">
    <el-card class="box-card">
      <!-- <template #header>
        <div class="card-header">
          <span>用户管理控制台</span>
        </div>
      </template> -->
      <el-table
        :data="users"
        style="width: 100%; margin-top: 20px"
        v-loading="loading"
        element-loading-text="加载中..."
      >
        <el-table-column prop="id" label="用户ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="role" label="角色" width="100" />
        <el-table-column prop="max_bots" label="最大机器人数量" width="150" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button
              type="danger"
              size="small"
              @click="deleteUser(scope.row.id)"
              :loading="loadingDelete[scope.row.id]"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { getUsers, deleteUser } from "@/utils/request";

const users = ref([]);
const loading = ref(false);
const loadingDelete = reactive({});

const fetchUsers = async () => {
  loading.value = true;
  try {
    const response = await getUsers();
    if (response.success) {
      users.value = response.data || [];
    } else {
      throw new Error(response.message || "获取用户列表失败");
    }
  } catch (err) {
    ElMessage.error(err.message);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchUsers();
});
</script>

<style scoped></style>

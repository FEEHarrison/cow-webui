<template>
  <div class="user-management-console">
    <el-table
      :data="users"
      style="margin-top: 20px"
      v-loading="loading"
      element-loading-text="加载中..."
    >
      <el-table-column prop="id" label="用户ID" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="role" label="角色" width="100" />
      <el-table-column prop="max_bots" label="最大机器人数量" width="150" />
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="scope">
          <div class="action-box">
            <el-button
              type="primary"
              size="small"
              @click="openEditDialog(scope.row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDeleteUser(scope.row.id)"
              :loading="loadingDelete[scope.row.id]"
            >
              删除
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="editDialogVisible"
      title="编辑用户"
      width="30%"
      append-to-body
    >
      <el-form :model="editingUser" label-width="120px">
        <el-form-item label="用户名">
          <el-input v-model="editingUser.username" disabled></el-input>
        </el-form-item>
        <el-form-item label="最大机器人数量">
          <el-input-number
            v-model="editingUser.max_bots"
            :min="-1"
          ></el-input-number>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveUserEdit" :loading="loading">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { getUsers, deleteUser } from "@/utils/request";
import { update_user_max_bots } from "@/api/user";

const users = ref([]);
const loading = ref(false);
const loadingDelete = reactive({});
const editingUser = ref({});
const editDialogVisible = ref(false);

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
const openEditDialog = (user) => {
  editingUser.value = { ...user };
  editDialogVisible.value = true;
};

const saveUserEdit = async () => {
  if (loading.value) return;
  loading.value = true;

  try {
    const response = await update_user_max_bots({
      user_id: editingUser.value.id,
      max_bots: editingUser.value.max_bots,
    });
    if (response.success && response.code === 200) {
      ElMessage.success("用户信息更新成功");
      editDialogVisible.value = false;
      await fetchUsers();
    } else {
      throw new Error(response.message || "更新用户信息失败");
    }
  } catch (err) {
    ElMessage.error(err.message);
  } finally {
    loading.value = false;
  }
};
const handleDeleteUser = async (userId) => {
  try {
    await ElMessageBox.confirm("确定要删除该用户吗？", "警告", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });

    loadingDelete[userId] = true;
    const response = await deleteUser(userId);
    if (response.success) {
      ElMessage.success("用户删除成功");
      await fetchUsers(); // 刷新用户列表
    } else {
      throw new Error(response.message || "删除用户失败");
    }
  } catch (err) {
    if (err !== "cancel") {
      ElMessage.error(err.message);
    }
  } finally {
    loadingDelete[userId] = false;
  }
};

onMounted(() => {
  fetchUsers();
});
</script>

<style scoped>
.user-management-console {
  overflow: auto;
}
.action-box {
  display: flex;
  flex-wrap: nowrap;
}
</style>

<template>
  <div class="bot-management-console">
    <el-container>
      <!-- <el-header>
        <h2>机器人管理控制台</h2>
      </el-header> -->
      <el-main>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-button
              type="primary"
              @click="showConfigDialog"
              class="custom-button"
              >创建wx机器人</el-button
            >
          </el-col>
        </el-row>

        <!-- 数据列表 -->
        <el-table
          :data="bots"
          class="custom-table"
          style="width: 100%; margin-top: 20px"
        >
          <el-table-column
            prop="id"
            label="机器人ID"
            width="180"
            class="custom-column"
          />
          <el-table-column
            prop="name"
            label="机器人名称"
            width="180"
            class="custom-column"
          />
          <el-table-column
            prop="qr_code_url"
            label="二维码"
            width="180"
            class="custom-column"
          >
            <template v-slot="scope">
              <el-button
                @click="getLogs(scope.row.id)"
                :loading="loadingLogs[scope.row.id]"
              >
                获取日志
              </el-button>
            </template>
          </el-table-column>
          <el-table-column
            prop="running"
            label="状态"
            width="100"
            class="custom-column"
          >
            <template v-slot="scope">
              <el-tag
                v-if="scope && scope.row"
                :type="scope.row.status ? 'success' : 'warning'"
                class="status-tag"
              >
                {{ scope.row.status == "running" ? "运行中" : "已停止" }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="240" class="custom-column">
            <template v-slot="scope">
              <el-button
                v-if="scope && scope.row"
                type="danger"
                size="small"
                @click="deleteBot(scope.row.id)"
                :loading="loadingDelete[scope.row.id]"
                class="action-button"
              >
                删除
              </el-button>
              <el-button
                v-if="scope && scope.row"
                type="primary"
                size="small"
                @click="restartBot(scope.row.id)"
                :loading="loadingRestart[scope.row.id]"
                class="action-button"
              >
                重启
              </el-button>
              <el-button
                v-if="scope && scope.row"
                type="primary"
                size="small"
                @click="showConfigDialog(scope.row)"
                :loading="loadingConfig[scope.row.id]"
                class="action-button"
              >
                查看配置
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-dialog
          v-model="dialogVisible"
          class="dialogStyle"
          @close="closeDialog"
          :fullscreen="false"
          :modal="true"
          :append-to-body="true"
        >
          <div
            class="dialog-content"
            style="max-height: 40vh; overflow-y: auto; text-align: center"
          >
            <div v-if="qrCodeUrl" class="qr-code-container">
              <img :src="qrCodeUrl" class="qr-image" />
              <p>请扫描二维码登录</p>
            </div>
            <div v-else-if="qrCodeUrl === null" class="no-qr-code">
              <p>未找到最近的二维码，请稍后再试</p>
            </div>
            <div class="log-container">
              <!-- <div v-for="(log, index) in logs" :key="index">{{ log }}</div> -->
              <div>{{ logs }}</div>
            </div>
          </div>
        </el-dialog>
        <ConfigDialog
          ref="configDialogRef"
          :createBot="createBot"
          :fetchBots="fetchBots"
        />

        <!-- 数据加载中的指示器 -->
        <el-loading :fullscreen="loading" v-if="loading"></el-loading>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from "vue";
import { ElMessage } from "element-plus";
import request from "@/utils/request";
import ConfigDialog from "@/components/Dialog.vue";
const configDialogRef = ref(null);
const bots = ref([]);
const loading = ref(false);
const error = ref(false);
const dialogVisible = ref(false); // 控制弹窗显示与隐藏
const qrCodeUrl = ref(""); // 存储二维码URL
const logs = ref([]);
const loadingLogs = reactive({});
const loadingDelete = reactive({});
const loadingRestart = reactive({});
const loadingConfig = reactive({});

const showConfigDialog = async (row) => {
  if (row.id) {
    loadingConfig[row.id] = true;
    try {
      if (configDialogRef.value) {
        const response = await request.get(
          `/api/get_bot_config/${row.service_id}`
        );
        configDialogRef.value.openConfigDialog(response.data || {}, row);
      }
    } catch (error) {
      ElMessage.error("获取配置失败");
    } finally {
      loadingConfig[row.id] = false;
    }
  } else {
    configDialogRef.value.openConfigDialog({});
  }
};
const createBot = async (config) => {
  console.log(config);
  try {
    const response = await request.post("/api/create_bot", {
      ...config,
    });
    if (response.success && response.code === 200) {
      ElMessage.success("机器人创建成功");
      configDialogRef.value.closeDialog();
      fetchBots();
    } else {
      throw new Error(response.message || "机器人创建失败");
    }
  } catch (err) {
    ElMessage.error(err.message);
  }
};

const getLogs = async (id) => {
  dialogVisible.value = true;
  qrCodeUrl.value = undefined;
  logs.value = [];
  loadingLogs[id] = true;

  try {
    const response = await request.get(`/api/logs/${id}`);
    if (response.success && response.code === 200) {
      qrCodeUrl.value = response.data.qr_code;
      logs.value = response.data.logs;
    } else {
      throw new Error(response.message || "获取日志失败");
    }
  } catch (error) {
    ElMessage.error("获取日志数据失败");
    console.error("获取日志数据失败:", error);
  } finally {
    loadingLogs[id] = false;
  }
};
const closeDialog = () => {
  qrCodeUrl.value = ""; // 清空二维码URL
  dialogVisible.value = false; // 隐藏弹窗
};
const fetchBots = async () => {
  loading.value = true;
  error.value = false;
  try {
    const response = await request.get("/api/bots");
    if (response.success && response.code === 200) {
      bots.value =
        response.data.map((item) => ({
          ...item,
          bot_name: item.config.BOT_NAME,
        })) || [];
    } else {
      throw new Error(response.message || "获取机器人列表失败");
    }
  } catch (err) {
    ElMessage.error(err.message);
    error.value = true;
  } finally {
    loading.value = false;
  }
};

const restartBot = async (id) => {
  loadingRestart[id] = true;
  try {
    const response = await request.post(`/api/restart_bot/${id}`);
    if (response.success && response.code === 200) {
      ElMessage.success("机器人重启成功,请扫描二维码");
      fetchBots();
    } else {
      throw new Error(response.message || "机器人重启失败");
    }
  } catch (err) {
    ElMessage.error(err.message);
  } finally {
    loadingRestart[id] = false;
  }
};

const deleteBot = async (bot_id) => {
  loadingDelete[bot_id] = true;
  try {
    const response = await request.delete(`/api/delete_bot/${bot_id}`);
    if (response.success && response.code === 200) {
      ElMessage.success("机器人删除成功");
      fetchBots();
    } else {
      throw new Error(response.message || "机器人删除失败");
    }
  } catch (err) {
    ElMessage.error(err.message);
  } finally {
    loadingDelete[bot_id] = false;
  }
};

onMounted(() => {
  fetchBots();
});
</script>

<style scoped>
.dialogStyle {
  :global(.el-dialog__body) {
    max-height: 200px;
    overflow: hidden;
  }
}
/* General Styles */
</style>

<template>
  <el-dialog
    v-model="dialogVisible"
    :title="containerId ? '编辑配置' : '创建机器人'"
    width="50%"
    @close="closeDialog"
  >
    <el-form :model="config" label-width="150px">
      <el-form-item label="机器人名称">
        <el-input
          v-model="config.BOT_NAME"
          placeholder="输入机器人名称"
        ></el-input>
      </el-form-item>
      <el-form-item label="模型">
        <el-select v-model="config.MODEL" placeholder="请选择模型">
          <el-option label="GPT-4o" value="gpt-4o"></el-option>
          <el-option label="GPT-3.5-Turbo" value="gpt-3.5-turbo"></el-option>
          <!-- Add more options if needed -->
        </el-select>
      </el-form-item>
      <el-form-item label="OpenAI API Key">
        <el-input v-model="config.OPEN_AI_API_KEY"></el-input>
      </el-form-item>
      <el-form-item label="OpenAI API Base">
        <el-input v-model="config.OPEN_AI_API_BASE"></el-input>
      </el-form-item>
      <el-form-item label="单聊前缀">
        <!-- <el-input v-model="config.SINGLE_CHAT_PREFIX"></el-input> -->
        <el-input
          v-model="config.SINGLE_CHAT_PREFIX"
          placeholder="输入以逗号分隔的前缀"
        ></el-input>
      </el-form-item>
      <el-form-item label="单聊回复前缀">
        <el-input
          v-model="config.SINGLE_CHAT_REPLY_PREFIX"
          placeholder="输入以逗号分隔的前缀"
        ></el-input>
      </el-form-item>
      <el-form-item label="群聊前缀">
        <el-input
          v-model="config.GROUP_CHAT_PREFIX"
          placeholder="输入以逗号分隔的前缀"
        ></el-input>
      </el-form-item>
      <el-form-item label="群组名称白名单">
        <el-input
          v-model="config.GROUP_NAME_WHITE_LIST"
          placeholder="输入以逗号分隔的前缀输入ALL_GROUP表示全部群组"
        ></el-input>
      </el-form-item>

      <el-form-item label="最大对话Token数">
        <el-input-number
          v-model="config.CONVERSATION_MAX_TOKENS"
        ></el-input-number>
      </el-form-item>
      <!-- <el-form-item label="过期时间(秒)">
        <el-input-number v-model="config.EXPIRES_IN_SECONDS"></el-input-number>
      </el-form-item> -->
      <el-form-item label="角色描述">
        <el-input
          type="textarea"
          autosize
          v-model="config.CHARACTER_DESC"
        ></el-input>
      </el-form-item>
      <el-form-item label="温度">
        <el-slider
          v-model="config.TEMPERATURE"
          :min="0"
          :max="1"
          step="0.01"
        ></el-slider>
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          @click="saveConfig"
          :loading="loading"
          :disabled="loading"
        >
          {{ containerId ? "保存配置" : "创建" }}
        </el-button>
        <el-button @click="closeDialog" :disabled="loading">取消</el-button>
      </el-form-item>
    </el-form>
  </el-dialog>
</template>

<script setup>
import { ref } from "vue";
// import { useLoading } from "@/hooks/useLoading.js";
import { ElMessage } from "element-plus";
import request from "@/utils/request";
import { defineProps } from "vue";

// 使用 defineProps 定义传递给子组件的方法
const props = defineProps({
  createBot: {
    type: Function,
    required: false,
  },
  fetchBots: {
    type: Function,
    required: false,
  },
});
const dialogVisible = ref(false);
const config = ref({});
const botId = ref(null);
// const { loading, withLoading } = useLoading();
const containerId = ref(null);
const loading = ref(false);
const openConfigDialog = async (data, row) => {
  dialogVisible.value = true;
  const new_config = data || {};
  console.log(row, "row");
  if (row) {
    config.value = {
      ...new_config,
      SINGLE_CHAT_PREFIX: (new_config?.SINGLE_CHAT_PREFIX || [])?.join(","),
      SINGLE_CHAT_REPLY_PREFIX: (
        new_config?.SINGLE_CHAT_REPLY_PREFIX || []
      )?.join(","),
      GROUP_CHAT_PREFIX: (new_config?.GROUP_CHAT_PREFIX || [])?.join(","),
      GROUP_NAME_WHITE_LIST: (new_config?.GROUP_NAME_WHITE_LIST || [])?.join(
        ","
      ),
    };
    botId.value = row.service_id;
    containerId.value = row.id;
  } else {
    containerId.value = "";
    config.value = {};
  }
};

const saveConfig = async () => {
  if (loading.value) return;
  loading.value = true;

  try {
    if (containerId.value) {
      const body = {
        ...config.value,
        SINGLE_CHAT_PREFIX: config?.value?.SINGLE_CHAT_PREFIX?.split(/[，,]/),
        SINGLE_CHAT_REPLY_PREFIX:
          config?.value?.SINGLE_CHAT_REPLY_PREFIX?.split(/[，,]/),
        GROUP_CHAT_PREFIX: config?.value?.GROUP_CHAT_PREFIX?.split(/[，,]/),
        GROUP_NAME_WHITE_LIST:
          config?.value?.GROUP_NAME_WHITE_LIST?.split(/[，,]/),
      };
      const response = await request.post(
        `/api/save_bot_config/${botId.value}`,
        body
      );
      if (response.success && response.code === 200) {
        ElMessage.success("配置保存成功");
        if (props.fetchBots) {
          await props.fetchBots();
        }
        dialogVisible.value = false;
      } else {
        throw new Error(response.message || "保存配置失败");
      }
    } else {
      if (props.createBot) {
        await props.createBot(config.value);
        dialogVisible.value = false;
      }
    }
  } catch (err) {
    ElMessage.error(err.message);
  } finally {
    loading.value = false;
  }
};

const closeDialog = () => {
  dialogVisible.value = false;
};
defineExpose({
  openConfigDialog,
  closeDialog,
});
</script>

<style scoped>
.el-dialog {
  padding: 20px;
}
</style>

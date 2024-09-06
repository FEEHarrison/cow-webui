<template>
  <el-dialog
    v-model="dialogVisible"
    :title="containerId ? '编辑配置' : '创建机器人'"
    width="70%"
    @close="closeDialog"
  >
    <el-form :model="config" label-width="150px">
      <el-form-item label="机器人名称">
        <el-input
          v-model="config.BOT_NAME"
          placeholder="输入机器人名称"
        ></el-input>
      </el-form-item>
      <el-form-item label="API平台">
        <el-select
          v-model="config.PLATFORM"
          placeholder="请选择API平台"
          @change="handlePlatformChange"
        >
          <el-option
            v-for="platform in platforms"
            :key="platform.value"
            :label="platform.label"
            :value="platform.value"
          ></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="模型">
        <el-select v-model="config.MODEL" placeholder="请选择模型">
          <el-option
            v-for="model in availableModels"
            :key="model.value"
            :label="model.label"
            :value="model.value"
          ></el-option>
        </el-select>
      </el-form-item>
      <template v-for="field in platformFields" :key="field.key">
        <el-form-item
          :label="field.label"
          v-if="config.PLATFORM === field.platform"
        >
          <el-input
            v-model="config[field.key]"
            :placeholder="field?.placeholder"
          ></el-input>
        </el-form-item>
      </template>
      <el-form-item label="单聊前缀">
        <el-input
          v-model="config.SINGLE_CHAT_PREFIX"
          placeholder="输入以逗号分隔的前缀"
        ></el-input>
      </el-form-item>
      <el-form-item label="单聊回复前缀">
        <el-input
          v-model="config.SINGLE_CHAT_REPLY_PREFIX"
          placeholder="输入私聊前缀"
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
import { ref, reactive, computed, watch } from "vue";
import { ElMessage } from "element-plus";
import request from "@/utils/request";
import { defineProps } from "vue";

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
const containerId = ref(null);
const loading = ref(false);

const platformsAndModels = reactive({
  openai: {
    label: "OpenAI",
    modelArr: [
      { label: "GPT-4o", value: "gpt-4o" },
      { label: "GPT-3.5-Turbo", value: "gpt-3.5-turbo" },
    ],
  },
  zhipuai: {
    label: "智谱AI",
    modelArr: [
      { label: "GLM-4", value: "GLM-4" },
      { label: "GLM-4-Flash", value: "GLM-4-Flash" },
      { label: "GLM-3-Turbo", value: "GLM-3-Turbo" },
    ],
  },
});

const platforms = computed(() =>
  Object.entries(platformsAndModels).map(([value, { label }]) => ({
    label,
    value,
  }))
);

const availableModels = computed(
  () => platformsAndModels[config.value.PLATFORM]?.modelArr || []
);

const platformFields = [
  { platform: "openai", key: "OPEN_AI_API_KEY", label: "OpenAI API Key" },
  { platform: "openai", key: "OPEN_AI_API_BASE", label: "OpenAI API Base" },
  { platform: "zhipuai", key: "ZHIPU_AI_API_KEY", label: "智谱AI API Key" },
  {
    platform: "zhipuai",
    key: "ZHIPU_AI_API_BASE",
    label: "智谱AI API Base",
    placeholder: "https://open.bigmodel.cn/api/paas/v4",
  },
  { platform: "tencent", key: "TENCENT_API_KEY", label: "腾讯混元 API Key" },
  { platform: "tencent", key: "TENCENT_API_BASE", label: "腾讯混元 API Base" },
];

const handlePlatformChange = (platform) => {
  config.value.MODEL = availableModels.value[0]?.value || "";
  platformFields.forEach((field) => {
    if (field.platform !== platform) {
      config.value[field.key] = "";
    }
  });
};

const openConfigDialog = async (data, row) => {
  dialogVisible.value = true;
  const new_config = data || {};
  if (row) {
    config.value = {
      ...new_config,
      SINGLE_CHAT_PREFIX: (new_config?.SINGLE_CHAT_PREFIX || [])?.join(","),
      GROUP_CHAT_PREFIX: (new_config?.GROUP_CHAT_PREFIX || [])?.join(","),
      GROUP_NAME_WHITE_LIST: (new_config?.GROUP_NAME_WHITE_LIST || [])?.join(
        ","
      ),
    };
    botId.value = row.service_id;
    containerId.value = row.id;
  } else {
    containerId.value = "";
    config.value = { PLATFORM: platforms.value[0]?.value || "" };
    handlePlatformChange(config.value.PLATFORM);
  }
};

const saveConfig = async () => {
  if (loading.value) return;
  loading.value = true;

  try {
    const body = {
      ...config.value,
      SINGLE_CHAT_PREFIX: config.value.SINGLE_CHAT_PREFIX?.split(/[，,]/),

      GROUP_CHAT_PREFIX: config.value.GROUP_CHAT_PREFIX?.split(/[，,]/),
      GROUP_NAME_WHITE_LIST: config.value.GROUP_NAME_WHITE_LIST?.split(/[，,]/),
    };

    platformFields.forEach((field) => {
      if (field.platform !== config.value.PLATFORM) {
        delete body[field.key];
      }
    });

    if (containerId.value) {
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
        await props.createBot(body);
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

watch(
  () => config.value.PLATFORM,
  (newPlatform) => {
    if (newPlatform && !config.value.MODEL) {
      config.value.MODEL = availableModels.value[0]?.value || "";
    }
  }
);

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

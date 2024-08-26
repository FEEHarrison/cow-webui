<template>
  <el-dialog
    v-model="dialogVisible"
    title="编辑配置"
    width="50%"
    @close="closeDialog"
  >
    <el-form :model="config" label-width="150px">
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
        <!-- <el-input
          v-for="(item, index) in ['xiazhus', 'dafsg']"
          :key="index"
          v-model="config.SINGLE_CHAT_PREFIX[index]"
        ></el-input> -->
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
        <el-button type="primary" @click="saveConfig">保存配置</el-button>
        <el-button @click="closeDialog">取消</el-button>
      </el-form-item>
    </el-form>
    <ElLoading :fullscreen="loading" v-if="loading"></ElLoading>
  </el-dialog>
</template>

<script setup>
import { ref } from "vue";
import { useLoading } from "@/hooks/useLoading.js";
import { ElMessage } from "element-plus";
import request from "@/utils/request";

const dialogVisible = ref(false);
const config = ref({});
const botId = ref(null);
const { loading, withLoading } = useLoading();

const openConfigDialog = async (data, id) => {
  dialogVisible.value = true;
  const new_config = data || {};
  console.log(new_config, new_config?.GROUP_NAME_WHITE_LIST);
  config.value = {
    ...new_config,
    SINGLE_CHAT_PREFIX: (new_config?.SINGLE_CHAT_PREFIX || [])?.join(","),
    SINGLE_CHAT_REPLY_PREFIX: (
      new_config?.SINGLE_CHAT_REPLY_PREFIX || []
    )?.join(","),
    GROUP_CHAT_PREFIX: (new_config?.GROUP_CHAT_PREFIX || [])?.join(","),
    GROUP_NAME_WHITE_LIST: (new_config?.GROUP_NAME_WHITE_LIST || [])?.join(","),
  };
  // botId.value = data.service_id;
  botId.value = id;
};

const saveConfig = async () => {
  const body = {
    ...config.value,
    SINGLE_CHAT_PREFIX: config?.value?.SINGLE_CHAT_PREFIX?.split(/[，,]/),
    SINGLE_CHAT_REPLY_PREFIX:
      config?.value?.SINGLE_CHAT_REPLY_PREFIX?.split(/[，,]/),
    GROUP_CHAT_PREFIX: config?.value?.GROUP_CHAT_PREFIX?.split(/[，,]/),
    GROUP_NAME_WHITE_LIST: config?.value?.GROUP_NAME_WHITE_LIST?.split(/[，,]/),
  };

  await withLoading(async () => {
    // console.log(body, "body");
    try {
      const response = await request.post(
        `/api/save_bot_config/${botId.value}`,
        body
      );
      if (response.success && response.code === 200) {
        ElMessage.success("配置保存成功");
        dialogVisible.value = false;
      } else {
        throw new Error(response.message || "保存配置失败");
      }
    } catch (err) {
      ElMessage.error(err.message);
    }
  });
};

const closeDialog = () => {
  dialogVisible.value = false;
};
defineExpose({
  openConfigDialog,
});
</script>

<style scoped>
.el-dialog {
  padding: 20px;
}
</style>

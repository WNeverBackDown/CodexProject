<script setup>
import { computed, onMounted, ref } from 'vue'
import { Eye, Plus, Send, Settings } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { api } from '../api/client'

const providers = ref([])
const channels = ref([])
const history = ref([])
const previewResult = ref(null)
const pushing = ref(false)

const channelForm = ref({
  name: '内部聊天机器人演示通道',
  provider: 'generic',
  robot_name: 'DataPulseBot',
  webhook_url: '',
  auth_type: 'none',
  secret_token: '',
  headers: {},
  payload_template: '',
  is_enabled: true,
  dry_run: true
})

const pushForm = ref({
  channel_id: null,
  provider: 'generic',
  title: 'DataPulse 日报',
  content: '今日查询量 18,240 次，AI 成功率 96.7%，高危异常 18 个。建议继续关注车联网投屏失败错误码 E102。',
  recipientsText: 'zhangsan\nlisi',
  message_format: 'markdown'
})

const recipientList = computed(() =>
  pushForm.value.recipientsText
    .split(/[\n,，;；\s]+/)
    .map((item) => item.trim())
    .filter(Boolean)
)

async function load() {
  const [providerRes, channelRes, historyRes] = await Promise.all([
    api.get('/api/reports/providers'),
    api.get('/api/reports/channels'),
    api.get('/api/reports/history')
  ])
  providers.value = providerRes.data
  channels.value = channelRes.data
  history.value = historyRes.data
  if (!pushForm.value.channel_id && channels.value.length) {
    pushForm.value.channel_id = channels.value[0].id
    pushForm.value.provider = channels.value[0].provider
  }
}

function selectedChannelChanged(id) {
  const channel = channels.value.find((item) => item.id === id)
  if (channel) pushForm.value.provider = channel.provider
}

async function createChannel() {
  const payload = {
    ...channelForm.value,
    webhook_url: channelForm.value.webhook_url || null,
    secret_token: channelForm.value.secret_token || null,
    payload_template: channelForm.value.payload_template || null
  }
  await api.post('/api/reports/channels', payload)
  ElMessage.success('报告推送通道已创建')
  await load()
}

function pushPayload() {
  return {
    title: pushForm.value.title,
    content: pushForm.value.content,
    recipients: recipientList.value,
    channel_id: pushForm.value.channel_id,
    provider: pushForm.value.provider,
    message_format: pushForm.value.message_format
  }
}

async function preview() {
  const res = await api.post('/api/reports/preview', pushPayload())
  previewResult.value = res.data
}

async function pushReport() {
  pushing.value = true
  try {
    const res = await api.post('/api/reports/push', pushPayload())
    previewResult.value = res.data.dispatch
    ElMessage.success(res.data.history.status === 'dry_run' ? '推送预演完成' : '报告推送已处理')
    await load()
  } finally {
    pushing.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="dashboard-main">
    <div class="page-grid">
      <section class="panel">
        <div class="panel-title"><Send :size="17" /> 报告推送</div>
        <div class="form-grid">
          <div class="two-col">
            <el-select v-model="pushForm.channel_id" placeholder="选择推送通道" class="full" @change="selectedChannelChanged">
              <el-option v-for="channel in channels" :key="channel.id" :label="`${channel.name} · ${channel.provider}${channel.dry_run ? ' · dry-run' : ''}`" :value="channel.id" />
            </el-select>
            <el-select v-model="pushForm.message_format" class="full">
              <el-option label="Markdown" value="markdown" />
              <el-option label="纯文本" value="text" />
            </el-select>
          </div>
          <el-input v-model="pushForm.title" placeholder="报告标题" />
          <el-input v-model="pushForm.content" type="textarea" :rows="7" placeholder="报告正文，支持 markdown 文本" />
          <el-input v-model="pushForm.recipientsText" type="textarea" :rows="3" placeholder="收件人账号、手机号或内部用户ID，每行一个" />
          <div class="toolbar">
            <el-button :icon="Eye" @click="preview">预览 payload</el-button>
            <el-button type="primary" :icon="Send" :loading="pushing" @click="pushReport">推送报告</el-button>
            <span class="muted">当前收件人 {{ recipientList.length }} 个；dry-run 通道不会真实发送。</span>
          </div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">推送预览 / 返回结果</div>
        <pre class="result-box">{{ previewResult || '点击预览或推送后查看机器人请求结构' }}</pre>
      </section>

      <section class="panel">
        <div class="panel-title">推送历史</div>
        <el-table :data="history" size="small" max-height="360">
          <el-table-column prop="title" label="报告" min-width="160" />
          <el-table-column prop="channel_name" label="通道" min-width="150" />
          <el-table-column prop="provider" label="平台" width="90" />
          <el-table-column prop="status" label="状态" width="100" />
          <el-table-column prop="created_by" label="创建人" width="110" />
        </el-table>
      </section>
    </div>

    <div class="page-grid">
      <section class="panel">
        <div class="panel-title"><Settings :size="17" /> 推送通道</div>
        <el-table :data="channels" size="small" max-height="250">
          <el-table-column prop="name" label="名称" min-width="160" />
          <el-table-column prop="provider" label="平台" width="92" />
          <el-table-column prop="robot_name" label="机器人" width="130" />
          <el-table-column prop="dry_run" label="预演" width="76">
            <template #default="{ row }">{{ row.dry_run ? '是' : '否' }}</template>
          </el-table-column>
        </el-table>
      </section>

      <section class="panel">
        <div class="panel-title"><Plus :size="17" /> 新增兼容通道</div>
        <div class="form-grid">
          <el-input v-model="channelForm.name" placeholder="通道名称" />
          <el-select v-model="channelForm.provider" class="full">
            <el-option v-for="provider in providers" :key="provider.key" :label="`${provider.name} · ${provider.key}`" :value="provider.key" />
          </el-select>
          <el-input v-model="channelForm.robot_name" placeholder="机器人名称" />
          <el-input v-model="channelForm.webhook_url" placeholder="Webhook URL，平台未确定可留空" />
          <el-select v-model="channelForm.auth_type" class="full">
            <el-option label="无认证" value="none" />
            <el-option label="Bearer Token" value="bearer" />
          </el-select>
          <el-input v-model="channelForm.secret_token" placeholder="密钥/Token，可留空" show-password />
          <el-switch v-model="channelForm.dry_run" active-text="dry-run 预演" inactive-text="真实发送" />
          <el-button type="primary" :icon="Plus" @click="createChannel">创建通道</el-button>
        </div>
      </section>
    </div>
  </div>
</template>

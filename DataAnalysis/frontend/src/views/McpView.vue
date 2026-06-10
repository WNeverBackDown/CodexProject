<script setup>
import { onMounted, ref } from 'vue'
import { ServerCog, Tag } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { api } from '../api/client'

const services = ref([])
const defectId = ref('12345')
const defect = ref(null)

async function load() {
  const res = await api.get('/api/mcp/services')
  services.value = res.data
}

async function queryDefect() {
  const res = await api.post('/api/mcp/noah-defect/query', { defect_id: defectId.value })
  defect.value = res.data
}

async function addLabel() {
  await api.post('/api/mcp/noah-defect/label', { defect_id: defectId.value, label: '埋点大数据监控' })
  ElMessage.success('标签已添加')
}

onMounted(load)
</script>

<template>
  <div class="dashboard-main">
    <section class="panel">
      <div class="panel-title"><ServerCog :size="17" /> MCP服务</div>
      <el-table :data="services">
        <el-table-column prop="name" label="服务" />
        <el-table-column prop="status" label="状态" width="120" />
        <el-table-column label="能力">
          <template #default="{ row }">{{ row.capabilities.join('、') }}</template>
        </el-table-column>
      </el-table>
    </section>
    <section class="panel">
      <div class="panel-title"><Tag :size="17" /> 诺亚缺陷演示</div>
      <div class="toolbar">
        <el-input v-model="defectId" style="width: 180px" />
        <el-button type="primary" @click="queryDefect">查询缺陷</el-button>
        <el-button @click="addLabel">添加标签</el-button>
      </div>
      <pre class="result-box">{{ defect || '暂无缺陷数据' }}</pre>
    </section>
  </div>
</template>

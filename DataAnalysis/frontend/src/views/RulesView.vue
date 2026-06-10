<script setup>
import { onMounted, ref } from 'vue'
import { Play, Plus, Workflow } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { api } from '../api/client'

const rules = ref([])
const histories = ref([])
const activeRule = ref(null)
const draft = ref({
  name: '车机投屏失败链路排查',
  description: '按 IMEI 聚合异常并分化错误码',
  status: 'published',
  split_field: 'error_code',
  steps: [
    { name: '定位异常IMEI', sql: "select imei, sum(cnt) as fail_cnt from dwd_vehicle_event_di group by imei" },
    { name: '错误码分布', sql: "select error_code, sum(cnt) as cnt from dwd_vehicle_event_di group by error_code" }
  ]
})

async function loadRules() {
  const res = await api.get('/api/rules/chain')
  rules.value = res.data
  activeRule.value ||= rules.value[0]
}

async function createRule() {
  const res = await api.post('/api/rules/chain', draft.value)
  rules.value.unshift(res.data)
  ElMessage.success('规则已创建')
}

async function executeRule(rule) {
  const res = await api.post('/api/rules/chain/execute', { rule_id: rule.id })
  ElMessage.success(res.data.summary)
  const historyRes = await api.get(`/api/rules/chain/${rule.id}/history`)
  histories.value = historyRes.data
}

onMounted(loadRules)
</script>

<template>
  <div class="dashboard-main">
    <section class="panel">
      <div class="panel-title"><Workflow :size="17" /> 链式规则列表</div>
      <div class="toolbar">
        <el-button type="primary" :icon="Plus" @click="createRule">按模板创建</el-button>
      </div>
      <el-table :data="rules" highlight-current-row @current-change="activeRule = $event">
        <el-table-column prop="name" label="规则" min-width="220" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="split_field" label="分化字段" width="120" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" :icon="Play" @click="executeRule(row)">执行</el-button>
          </template>
        </el-table-column>
      </el-table>
    </section>
    <div class="page-grid">
      <section class="panel">
        <div class="panel-title">规则步骤</div>
        <el-steps direction="vertical" :active="activeRule?.steps?.length || 0" finish-status="success">
          <el-step v-for="step in activeRule?.steps || []" :key="step.name" :title="step.name" :description="step.sql" />
        </el-steps>
      </section>
      <section class="panel">
        <div class="panel-title">执行历史</div>
        <el-table :data="histories" size="small">
          <el-table-column prop="status" label="状态" width="90" />
          <el-table-column prop="duration_ms" label="耗时" width="90" />
          <el-table-column prop="summary" label="摘要" />
        </el-table>
      </section>
    </div>
  </div>
</template>

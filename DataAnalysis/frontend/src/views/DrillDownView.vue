<script setup>
import { ref } from 'vue'
import { GitBranch, Save, Sparkles } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { api } from '../api/client'
import DataSourcePicker from '../components/DataSourcePicker.vue'

const picker = ref()
const field = ref('error_code')
const distribution = ref(null)
const recommendations = ref([])
const sessions = ref([])

async function runDistribution() {
  const res = await api.post('/api/ai/drill-down/analyze-distribution', { field: field.value, table_name: picker.value?.selectedTable || 'dwd_vehicle_event_di' })
  distribution.value = res.data
}

async function recommend() {
  const res = await api.post('/api/ai/drill-down/analyze', { table_name: picker.value?.selectedTable || 'dwd_vehicle_event_di' })
  recommendations.value = res.data.recommendations
}

async function saveSession() {
  const res = await api.post('/api/ai/drill-down/save-session', {
    title: `${field.value} 下钻会话`,
    table_name: picker.value?.selectedTable || 'dwd_vehicle_event_di',
    state: { field: field.value, distribution: distribution.value, recommendations: recommendations.value }
  })
  sessions.value.unshift(res.data)
  ElMessage.success('会话已保存')
}
</script>

<template>
  <div class="dashboard-main">
    <div class="page-grid">
      <section class="panel">
        <div class="panel-title"><GitBranch :size="17" /> 下钻控制台</div>
        <div class="toolbar">
          <el-input v-model="field" style="width: 220px" placeholder="字段名" />
          <el-button type="primary" :icon="Sparkles" @click="runDistribution">分析分布</el-button>
          <el-button @click="recommend">智能推荐</el-button>
          <el-button :icon="Save" @click="saveSession">保存会话</el-button>
        </div>
      </section>
      <section class="panel">
        <div class="panel-title">字段分布</div>
        <el-table :data="distribution?.values || []">
          <el-table-column prop="value" label="取值" />
          <el-table-column prop="count" label="次数" />
          <el-table-column prop="ratio" label="占比">
            <template #default="{ row }">{{ Math.round(row.ratio * 100) }}%</template>
          </el-table-column>
        </el-table>
        <p class="muted">{{ distribution?.insight }}</p>
      </section>
      <section class="panel">
        <div class="panel-title">推荐方向</div>
        <div class="insight-list">
          <div v-for="item in recommendations" :key="item.field" class="insight-item">
            <strong>{{ item.field }}</strong> · {{ item.reason }} · {{ item.next_step }}
          </div>
        </div>
      </section>
    </div>
    <div class="page-grid">
      <DataSourcePicker ref="picker" />
      <section class="panel">
        <div class="panel-title">当前保存会话</div>
        <div v-for="session in sessions" :key="session.id" class="insight-item">{{ session.title }} · {{ session.table_name }}</div>
      </section>
    </div>
  </div>
</template>

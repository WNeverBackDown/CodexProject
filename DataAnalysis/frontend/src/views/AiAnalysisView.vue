<script setup>
import { onMounted, ref } from 'vue'
import { Bot, Play, WandSparkles } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { api } from '../api/client'
import DataSourcePicker from '../components/DataSourcePicker.vue'

const picker = ref()
const models = ref([])
const history = ref([])
const form = ref({ question: '分析车联网投屏失败错误码分布', model_name: 'DataPulse-Demo-Agent' })
const result = ref(null)
const generatedSql = ref('')
const loading = ref(false)

async function load() {
  const [modelRes, historyRes] = await Promise.all([api.get('/api/ai/models'), api.get('/api/ai/history')])
  models.value = modelRes.data
  history.value = historyRes.data
}

async function generateSql() {
  const res = await api.post('/api/ai/generate-sql', {
    question: form.value.question,
    table_name: picker.value?.selectedTable || 'dwd_vehicle_event_di'
  })
  generatedSql.value = res.data.sql
}

async function analyze() {
  loading.value = true
  try {
    const res = await api.post('/api/ai/analyze', {
      question: form.value.question,
      model_name: form.value.model_name,
      table_name: picker.value?.selectedTable || 'dwd_vehicle_event_di'
    })
    result.value = res.data
    generatedSql.value = res.data.sql
    ElMessage.success('AI分析完成')
    load()
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="dashboard-main">
    <div class="page-grid">
      <section class="panel">
        <div class="panel-title"><Bot :size="17" /> AI分析工作台</div>
        <div class="form-grid">
          <el-select v-model="form.model_name" class="full">
            <el-option v-for="model in models" :key="model.name" :label="`${model.name} · ${model.capability}`" :value="model.name" />
          </el-select>
          <el-input v-model="form.question" type="textarea" :rows="4" placeholder="输入自然语言分析问题" />
          <div class="toolbar">
            <el-button :icon="WandSparkles" @click="generateSql">生成SQL</el-button>
            <el-button type="primary" :icon="Play" :loading="loading" @click="analyze">执行AI分析</el-button>
          </div>
        </div>
      </section>
      <section class="panel">
        <div class="panel-title">生成SQL</div>
        <pre class="sql-box">{{ generatedSql || '等待生成 SQL' }}</pre>
      </section>
      <section class="panel">
        <div class="panel-title">分析结果</div>
        <pre class="result-box">{{ result || '暂无结果' }}</pre>
      </section>
    </div>
    <div class="page-grid">
      <DataSourcePicker ref="picker" />
      <section class="panel">
        <div class="panel-title">分析历史</div>
        <el-table :data="history" size="small" max-height="430">
          <el-table-column prop="question" label="问题" min-width="180" />
          <el-table-column prop="model_name" label="模型" width="170" />
        </el-table>
      </section>
    </div>
  </div>
</template>

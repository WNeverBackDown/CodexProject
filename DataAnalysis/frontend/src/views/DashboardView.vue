<script setup>
import { computed, onMounted, ref } from 'vue'
import { Activity, BrainCircuit, Clock3 } from 'lucide-vue-next'
import { api } from '../api/client'
import ChartPanel from '../components/ChartPanel.vue'
import MetricCard from '../components/MetricCard.vue'

const overview = ref({ metrics: [], trend: [], domains: [], ai_insights: [] })
const statistics = ref({ model_health: [], rule_timeline: [] })

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 38, right: 16, bottom: 28, top: 26 },
  xAxis: { type: 'category', data: overview.value.trend.map((item) => item.label) },
  yAxis: { type: 'value' },
  series: [{ type: 'line', smooth: true, areaStyle: {}, color: '#2563eb', data: overview.value.trend.map((item) => item.value) }]
}))

const domainOption = computed(() => ({
  tooltip: {},
  grid: { left: 64, right: 18, bottom: 26, top: 18 },
  xAxis: { type: 'value' },
  yAxis: { type: 'category', data: overview.value.domains.map((item) => item.label) },
  series: [{ type: 'bar', color: '#0891b2', data: overview.value.domains.map((item) => item.value) }]
}))

onMounted(async () => {
  const [overviewRes, statisticsRes] = await Promise.all([api.get('/api/dashboard/overview'), api.get('/api/dashboard/statistics')])
  overview.value = overviewRes.data
  statistics.value = statisticsRes.data
})
</script>

<template>
  <div class="page-grid">
    <div class="kpi-grid">
      <MetricCard v-for="metric in overview.metrics" :key="metric.code" :metric="metric" />
    </div>
    <div class="dashboard-main">
      <ChartPanel title="查询与异常趋势" :option="trendOption" />
      <section class="panel">
        <div class="panel-title"><BrainCircuit :size="17" /> AI洞察</div>
        <div class="insight-list">
          <div v-for="item in overview.ai_insights" :key="item" class="insight-item">{{ item }}</div>
        </div>
      </section>
    </div>
    <div class="two-col">
      <ChartPanel title="业务领域数据量" :option="domainOption" />
      <section class="panel">
        <div class="panel-title"><Activity :size="17" /> 模型健康</div>
        <el-table :data="statistics.model_health" size="small">
          <el-table-column prop="name" label="模型" min-width="170" />
          <el-table-column prop="success" label="成功率" width="96">
            <template #default="{ row }">{{ row.success }}%</template>
          </el-table-column>
          <el-table-column prop="latency" label="延迟" width="86">
            <template #default="{ row }">{{ row.latency }}ms</template>
          </el-table-column>
        </el-table>
      </section>
    </div>
    <section class="panel">
      <div class="panel-title"><Clock3 :size="17" /> 规则执行动态</div>
      <el-timeline>
        <el-timeline-item v-for="item in statistics.rule_timeline" :key="item.time" :timestamp="item.time" :type="item.status === 'warning' ? 'warning' : 'success'">
          {{ item.name }} · {{ item.status }}
        </el-timeline-item>
      </el-timeline>
    </section>
  </div>
</template>

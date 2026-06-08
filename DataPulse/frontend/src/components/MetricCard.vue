<script setup>
import { TrendingDown, TrendingUp } from 'lucide-vue-next'

defineProps({
  metric: { type: Object, required: true }
})
</script>

<template>
  <section class="metric-card">
    <div class="metric-header">
      <span>{{ metric.name }}</span>
      <el-tag :type="metric.status === 'warning' ? 'warning' : 'success'" size="small" effect="plain">
        {{ metric.status === 'warning' ? '关注' : '稳定' }}
      </el-tag>
    </div>
    <div class="metric-value">{{ Number(metric.value).toLocaleString() }}<small>{{ metric.unit }}</small></div>
    <div :class="['metric-trend', metric.trend >= 0 ? 'up' : 'down']">
      <TrendingUp v-if="metric.trend >= 0" :size="15" />
      <TrendingDown v-else :size="15" />
      <span>{{ Math.abs(metric.trend) }}% 较昨日</span>
    </div>
  </section>
</template>

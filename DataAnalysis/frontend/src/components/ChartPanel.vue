<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  title: { type: String, required: true },
  option: { type: Object, required: true }
})

const el = ref()
let chart

function render() {
  if (!el.value) return
  chart ||= echarts.init(el.value)
  chart.setOption(props.option, true)
}

function resize() {
  chart?.resize()
}

onMounted(() => {
  render()
  window.addEventListener('resize', resize)
})
watch(() => props.option, render, { deep: true })
onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chart?.dispose()
})
</script>

<template>
  <section class="panel chart-panel">
    <div class="panel-title">{{ title }}</div>
    <div ref="el" class="chart-canvas" />
  </section>
</template>

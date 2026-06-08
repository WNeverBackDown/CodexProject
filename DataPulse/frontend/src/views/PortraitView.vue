<script setup>
import { onMounted, ref } from 'vue'
import { Play, UserRoundSearch } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { api } from '../api/client'

const configs = ref([])
const imeis = ref([])
const profile = ref({ domains: [] })
const activeImei = ref('860000000000001')

async function load() {
  const [configRes, imeiRes, profileRes] = await Promise.all([
    api.get('/api/user-portrait/behavior-config'),
    api.get('/api/user-portrait/monitor-imei'),
    api.get('/api/user-portrait/user-behavior/user-profile', { params: { imei: activeImei.value } })
  ])
  configs.value = configRes.data
  imeis.value = imeiRes.data
  profile.value = profileRes.data
}

async function execute() {
  await api.post('/api/user-portrait/monitor-imei/execute', { imei: activeImei.value, label: '实时执行', config_ids: configs.value.map((item) => item.id) })
  ElMessage.success('画像配置执行完成')
  load()
}

onMounted(load)
</script>

<template>
  <div class="three-col">
    <section class="panel">
      <div class="panel-title"><UserRoundSearch :size="17" /> 行为配置</div>
      <div v-for="item in configs" :key="item.id" class="insight-item">
        <strong>{{ item.name }}</strong><br />
        <span class="muted">{{ item.domain }} · {{ item.db_name }}</span>
      </div>
    </section>
    <section class="panel">
      <div class="panel-title">IMEI监控</div>
      <el-select v-model="activeImei" class="full" @change="load">
        <el-option v-for="item in imeis" :key="item.id" :label="`${item.imei} · ${item.label}`" :value="item.imei" />
      </el-select>
      <div class="toolbar" style="margin-top: 12px">
        <el-button type="primary" :icon="Play" @click="execute">执行配置</el-button>
      </div>
      <el-table :data="imeis" size="small">
        <el-table-column prop="imei" label="IMEI" />
        <el-table-column prop="status" label="状态" width="90" />
      </el-table>
    </section>
    <section class="panel">
      <div class="panel-title">用户画像</div>
      <div v-for="domain in profile.domains" :key="domain.domain" class="insight-item">
        <strong>{{ domain.domain }}</strong> · 风险 {{ domain.risk }}
        <div v-for="behavior in domain.behaviors" :key="behavior.id" class="muted">
          {{ behavior.behavior_name }} · {{ behavior.risk_level }}
        </div>
      </div>
    </section>
  </div>
</template>

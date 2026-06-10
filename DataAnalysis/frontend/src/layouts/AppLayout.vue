<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Bot,
  FileText,
  GitBranch,
  LayoutDashboard,
  Search,
  ServerCog,
  UserRoundSearch,
  Users,
  Workflow
} from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'

const icons = { LayoutDashboard, Bot, FileText, GitBranch, Workflow, UserRoundSearch, ServerCog, Users }
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const title = computed(() => route.meta.title || '总览')

onMounted(() => auth.bootstrap())
</script>

<template>
  <div class="app-shell">
    <aside class="side-nav">
      <div class="brand">
        <div class="brand-mark">DP</div>
        <div>
          <strong>DataPulse</strong>
          <span>大数据AI分析</span>
        </div>
      </div>
      <nav class="nav-list">
        <button
          v-for="item in auth.menu"
          :key="item.path"
          :class="['nav-item', { active: route.path === item.path }]"
          @click="router.push(item.path)"
        >
          <component :is="icons[item.icon]" :size="18" />
          <span>{{ item.name }}</span>
        </button>
      </nav>
    </aside>
    <main class="main-area">
      <header class="top-bar">
        <div>
          <h1>{{ title }}</h1>
          <p>统一分析、下钻、规则执行与用户画像工作台</p>
        </div>
        <div class="top-actions">
          <div class="search-box"><Search :size="16" /><span>搜索数据源、规则、IMEI</span></div>
          <el-tag type="success" effect="plain">development</el-tag>
          <el-avatar :size="34">{{ auth.user?.display_name?.slice(0, 1) || 'D' }}</el-avatar>
        </div>
      </header>
      <router-view />
    </main>
  </div>
</template>

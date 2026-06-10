import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '../layouts/AppLayout.vue'
import DashboardView from '../views/DashboardView.vue'
import AiAnalysisView from '../views/AiAnalysisView.vue'
import DrillDownView from '../views/DrillDownView.vue'
import RulesView from '../views/RulesView.vue'
import PortraitView from '../views/PortraitView.vue'
import ReportPushView from '../views/ReportPushView.vue'
import McpView from '../views/McpView.vue'
import UsersView from '../views/UsersView.vue'

const routes = [
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '', component: DashboardView, meta: { title: '总览' } },
      { path: 'ai', component: AiAnalysisView, meta: { title: 'AI分析' } },
      { path: 'drill-down', component: DrillDownView, meta: { title: '下钻分析' } },
      { path: 'rules', component: RulesView, meta: { title: '链式规则' } },
      { path: 'portrait', component: PortraitView, meta: { title: '用户画像' } },
      { path: 'reports', component: ReportPushView, meta: { title: '报告推送' } },
      { path: 'mcp', component: McpView, meta: { title: 'MCP服务' } },
      { path: 'users', component: UsersView, meta: { title: '用户管理' } }
    ]
  }
]

export default createRouter({
  history: createWebHistory(),
  routes
})

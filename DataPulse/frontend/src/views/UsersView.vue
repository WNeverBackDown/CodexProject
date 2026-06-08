<script setup>
import { onMounted, ref } from 'vue'
import { Users } from 'lucide-vue-next'
import { api } from '../api/client'

const users = ref([])
onMounted(async () => {
  const res = await api.get('/api/auth/users')
  users.value = res.data
})
</script>

<template>
  <section class="panel">
    <div class="panel-title"><Users :size="17" /> 用户信息管理</div>
    <el-table :data="users">
      <el-table-column prop="uid" label="UID" width="150" />
      <el-table-column prop="display_name" label="姓名" width="130" />
      <el-table-column prop="department" label="部门" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <span><i class="status-dot" />{{ row.is_active ? '启用' : '停用' }}</span>
        </template>
      </el-table-column>
    </el-table>
  </section>
</template>

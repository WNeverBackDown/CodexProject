<script setup>
import { onMounted } from 'vue'
import { Database } from 'lucide-vue-next'
import { useDatabaseSelector } from '../composables/useDatabaseSelector'

const {
  databases,
  tables,
  selectedDatabase,
  selectedType,
  selectedTable,
  keyword,
  loading,
  filteredDatabases,
  loadDatabases,
  selectDatabase
} = useDatabaseSelector()

defineExpose({ databases, tables, selectedDatabase, selectedType, selectedTable, keyword, loading, filteredDatabases, loadDatabases, selectDatabase })
onMounted(loadDatabases)
</script>

<template>
  <section class="panel">
    <div class="panel-title with-icon"><Database :size="17" /> 数据源</div>
    <el-input v-model="keyword" placeholder="搜索数据库" clearable />
    <div class="database-list">
      <button
        v-for="item in filteredDatabases"
        :key="`${item.type}-${item.db_name}`"
        :class="['database-item', { active: selectedDatabase === item.db_name }]"
        @click="selectDatabase(item)"
      >
        <strong>{{ item.db_name }}</strong>
        <span>{{ item.type }} · {{ item.description }}</span>
      </button>
    </div>
    <el-select v-model="selectedTable" placeholder="选择数据表" class="full">
      <el-option v-for="table in tables" :key="table.table_name" :label="table.table_name" :value="table.table_name" />
    </el-select>
  </section>
</template>

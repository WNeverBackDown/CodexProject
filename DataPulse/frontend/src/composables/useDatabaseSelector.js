import { computed, ref } from 'vue'
import { api } from '../api/client'

export function useDatabaseSelector() {
  const databases = ref([])
  const tables = ref([])
  const selectedDatabase = ref('')
  const selectedType = ref('')
  const selectedTable = ref('')
  const keyword = ref('')
  const loading = ref(false)

  const filteredDatabases = computed(() => {
    const k = keyword.value.trim().toLowerCase()
    if (!k) return databases.value
    return databases.value.filter((item) => `${item.db_name} ${item.type} ${item.description || ''}`.toLowerCase().includes(k))
  })

  async function loadDatabases() {
    loading.value = true
    try {
      const res = await api.get('/api/ai/databases')
      databases.value = res.data
      if (!selectedDatabase.value && databases.value.length) {
        selectDatabase(databases.value[0])
      }
    } finally {
      loading.value = false
    }
  }

  async function selectDatabase(item) {
    selectedDatabase.value = item.db_name
    selectedType.value = item.type
    const res = await api.get('/api/ai/tables', { params: { db_name: item.db_name, db_type: item.type } })
    tables.value = res.data
    selectedTable.value = tables.value[0]?.table_name || ''
  }

  return {
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
  }
}

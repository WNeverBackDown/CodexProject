# useDatabaseSelector

封装 AI 分析与下钻分析共用的数据源选择逻辑：

- `loadDatabases()` 加载数据库列表并自动选中首个可用库。
- `selectDatabase(item)` 根据库名和类型加载表列表。
- `filteredDatabases` 根据关键字过滤库名、类型和描述。

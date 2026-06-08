export const heroFacts = [
  ['面向成效做特征识别', '围绕真实业务人群和结果指标，抽取可迁移的画像、行为和约束。', 'blue'],
  ['Agent 自动完成任务闭环', '从需求拆解到 Prompt 检索、模型执行、Judge 决策和提交。', 'blue'],
  ['自研 Prompt 搜索、特征迭代、指标评估', '把经验沉淀成可复用资产，并通过离线指标持续筛优。', 'blue'],
  ['Judge 决策，自动提交 MR', '按阈值检查质量、成本和风险，输出可审查提交包。', 'navy'],
]

export const kpis = [
  ['人力耗时', '3人日 -> 3小时', '需求理解、Prompt 改写、评估压缩到单次闭环'],
  ['离线 AUC', '0.76 -> 0.82', '稳定找到更优 prompt 与人群特征组合'],
  ['单日 token 成本', '约 50 元', '通过缓存、候选裁剪和分层评估控制成本'],
  ['上线状态', '生产可用', '保留审查、回滚和指标归因链路'],
]

export const painPoints = [
  ['需求变化快', '不知道业务方真实要找什么人，人工改 Prompt 往往要反复沟通。'],
  ['评估链路长', '特征、Prompt 和模型结果要人工串联，反馈周期长。'],
  ['上线不可控', '开发、评估、提交和回滚割裂，容易出现灰度断点。'],
  ['迁移成本高', '经验散落在个人和项目里，换场景后难复用。'],
]

export const principles = [
  ['搜索价值', '把人力投入到策略边界和指标解释，减少低价值调参。'],
  ['质量价值', '每一轮都有候选、评估和 Judge 记录，可复盘。'],
  ['成本价值', '使用候选剪枝、缓存和小样本验证降低 token 成本。'],
  ['复用价值', '把 prompt、特征和评估模板沉淀为可迁移资产。'],
]

export const agentNodes = [
  ['feature_extractor', 'feature_extractor', '特征抽取', '解析需求、样本和业务规则，生成可检索的人群特征。'],
  ['prompt_searcher', 'prompt_searcher', 'Prompt 迭代', '从模板库和历史成功案例中召回候选 Prompt。'],
  ['model_caller', 'model_caller', 'LLM 调用', '调用 DeepSeek 生成结构化候选方案、解释和特征权重。'],
  ['model_evaluator', 'model_evaluator', 'LLM 评估', '计算 AUC、precision、recall、成本和稳定性预估。'],
  ['judge_hook', 'judge_and_hook', '判断与触达', '按阈值做上线判断，并产出可审查的变更摘要。'],
  ['git_controller', 'git_controller', '提交 MR', '封装 Prompt、指标和回滚信息，生成提交包草案。'],
]

export const metrics = [
  ['人均处理时长', '3 人日', '3 小时', '24 倍提效'],
  ['任务完成率', '100%', '100%', '持平'],
  ['结果准确性', 'AUC 0.76', 'AUC 0.82', '+7.8%'],
  ['成本/token 消耗', '取决于人工成本', '约 50 元', '可控'],
]

export const chartPoints = [
  0.77, 0.8, 0.79, 0.795, 0.798, 0.801, 0.792, 0.789, 0.785, 0.783, 0.792,
  0.805, 0.812, 0.819, 0.821, 0.817, 0.824, 0.823, 0.71,
]

export const markets = ['电商增长', 'B 端销售', '金融理财', '本地生活']

export const deepseekModels = [
  ['deepseek-v4-flash', 'DeepSeek V4 Flash - 快速低成本'],
  ['deepseek-v4-pro', 'DeepSeek V4 Pro - 更强推理'],
  ['deepseek-chat', 'deepseek-chat - 兼容旧模型名'],
]

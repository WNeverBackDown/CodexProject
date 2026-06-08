export const promptBank = [
  {
    id: 'seg-growth',
    title: '高意向增长人群识别',
    source: '增长投放 Prompt 库',
    tactic: '提取购买意图、近期行为和预算敏感度，优先召回高转化人群。',
  },
  {
    id: 'seg-retention',
    title: '沉默用户召回分层',
    source: 'CRM 运营 Prompt 库',
    tactic: '按活跃衰减、品类偏好和优惠敏感度做分层触达。',
  },
  {
    id: 'seg-risk',
    title: '低质流量过滤',
    source: '风控 Prompt 库',
    tactic: '识别异常行为、低履约意愿和重复线索，降低坏样本污染。',
  },
  {
    id: 'seg-b2b',
    title: 'B 端线索优先级排序',
    source: '销售线索 Prompt 库',
    tactic: '结合行业、规模、决策链和近期需求强度生成线索评分。',
  },
]

const keywordFeatureMap = [
  [/母婴|宝妈|亲子|育儿/, '家庭生命周期'],
  [/高净值|理财|保险|金融/, '资产与风险偏好'],
  [/企业|B端|B 端|销售|线索|CRM/i, '企业决策链'],
  [/复购|留存|召回|沉默/, '活跃衰减与复购概率'],
  [/优惠|价格|折扣|成本/, '价格敏感度'],
  [/AUC|准确|评估|指标/i, '可量化评估目标'],
  [/上线|MR|发布|灰度/, '可审查交付约束'],
]

export function runLocalWorkflow(brief, market) {
  const normalized = brief.trim() || '为一个消费业务自动挖掘高转化人群，要求可评估、成本可控并能提交上线。'
  const features = extractFeatures(normalized, market)
  const candidatePrompts = rankPrompts(normalized, features)
  const selectedPrompt = candidatePrompts[0]
  const auc = Number((0.76 + Math.min(features.length, 7) * 0.008 + selectedPrompt.score / 1600).toFixed(3))
  const tokenCost = Math.max(28, Math.round(82 - selectedPrompt.score * 0.42))

  return normalizeAgentRun({
    source: 'local',
    summary: '本地规则引擎生成的预估结果。填入 DeepSeek API key 后可运行真实 LLM Agent。',
    features,
    candidatePrompts,
    selectedPrompt,
    judgeFindings: [
      `选择「${selectedPrompt.title}」，因为它覆盖 ${features.slice(0, 3).join('、')}。`,
      auc >= 0.82 ? '离线 AUC 预估达到上线阈值，允许生成提交包。' : 'AUC 接近阈值，建议补一轮负样本验证。',
      tokenCost <= 55 ? 'Token 成本在单日预算内，可进入灰度。' : '成本偏高，需缩小候选样本或开启缓存。',
    ],
    submission: {
      title: `${market} 人群挖掘 Prompt 优化包`,
      confidence: Math.min(96, Math.round(72 + selectedPrompt.score / 3)),
      auc,
      tokenCost,
      elapsedHours: Number((2.2 + features.length * 0.12).toFixed(1)),
      mrBody: [
        `业务场景：${market}`,
        `候选 Prompt：${selectedPrompt.title}`,
        `预估 AUC：${auc}`,
        '回滚条件：线上指标连续两个周期低于基线时回滚。',
      ],
    },
    evaluation: {
      auc,
      precision: Number(Math.min(0.91, auc - 0.03).toFixed(3)),
      recall: Number(Math.min(0.9, auc - 0.04).toFixed(3)),
      riskLevel: auc >= 0.82 ? 'low' : 'medium',
      notes: ['本地评估为可解释预估，不代表真实离线评估。'],
    },
    usage: null,
    rawModelText: '',
  })
}

export function normalizeAgentRun(input) {
  const candidatePrompts = Array.isArray(input?.candidatePrompts) && input.candidatePrompts.length
    ? input.candidatePrompts.map((item, index) => ({
        id: String(item.id || `prompt-${index + 1}`),
        title: String(item.title || `候选 Prompt ${index + 1}`),
        score: clampNumber(item.score, 0, 100, 75),
        source: String(item.source || 'DeepSeek 生成'),
        tactic: String(item.tactic || item.reason || '根据任务上下文生成的人群挖掘策略。'),
        prompt: String(item.prompt || ''),
      }))
    : runLocalWorkflow('', '通用场景').candidatePrompts

  const selectedPrompt = input?.selectedPrompt
    ? {
        id: String(input.selectedPrompt.id || candidatePrompts[0].id),
        title: String(input.selectedPrompt.title || candidatePrompts[0].title),
        score: clampNumber(input.selectedPrompt.score, 0, 100, candidatePrompts[0].score),
        source: String(input.selectedPrompt.source || candidatePrompts[0].source),
        tactic: String(input.selectedPrompt.tactic || candidatePrompts[0].tactic),
        prompt: String(input.selectedPrompt.prompt || candidatePrompts[0].prompt || ''),
      }
    : candidatePrompts[0]

  const auc = clampNumber(input?.submission?.auc ?? input?.evaluation?.auc, 0.5, 0.99, 0.82)
  const tokenCost = clampNumber(input?.submission?.tokenCost, 0, 9999, 50)

  return {
    source: input?.source || 'deepseek',
    summary: String(input?.summary || 'DeepSeek 已完成一次结构化 Agent 运行。'),
    features: normalizeStringArray(input?.features, ['业务上下文', '正负样本边界', 'Prompt 迁移约束']),
    candidatePrompts,
    selectedPrompt,
    judgeFindings: normalizeStringArray(input?.judgeFindings, ['指标达到试运行阈值。', '建议进入灰度并保留回滚条件。']),
    submission: {
      title: String(input?.submission?.title || '人群挖掘 Prompt 优化包'),
      confidence: clampNumber(input?.submission?.confidence, 0, 100, 86),
      auc,
      tokenCost,
      elapsedHours: clampNumber(input?.submission?.elapsedHours, 0, 999, 3),
      mrBody: normalizeStringArray(input?.submission?.mrBody, ['变更 Prompt、评估结果和回滚条件见本提交包。']),
    },
    evaluation: {
      auc,
      precision: clampNumber(input?.evaluation?.precision, 0, 1, Math.max(0.5, auc - 0.03)),
      recall: clampNumber(input?.evaluation?.recall, 0, 1, Math.max(0.5, auc - 0.04)),
      riskLevel: String(input?.evaluation?.riskLevel || (auc >= 0.82 ? 'low' : 'medium')),
      notes: normalizeStringArray(input?.evaluation?.notes, ['等待真实离线样本集复核。']),
    },
    usage: input?.usage || null,
    rawModelText: String(input?.rawModelText || ''),
  }
}

function extractFeatures(brief, market) {
  const mapped = keywordFeatureMap
    .filter(([pattern]) => pattern.test(brief))
    .map(([, feature]) => feature)

  return Array.from(
    new Set([
      `${market} 业务上下文`,
      ...mapped,
      '正负样本边界',
      'Prompt 可迁移约束',
      '上线回滚条件',
    ]),
  )
}

function rankPrompts(brief, features) {
  return promptBank
    .map((prompt) => {
      const base = prompt.id === 'seg-growth' ? 82 : 72
      const briefBonus = /B端|B 端|企业|销售|线索|CRM/i.test(brief) && prompt.id === 'seg-b2b' ? 15 : 0
      const retentionBonus = /复购|留存|召回|沉默/.test(brief) && prompt.id === 'seg-retention' ? 14 : 0
      const riskBonus = /低质|风控|过滤/.test(brief) && prompt.id === 'seg-risk' ? 14 : 0
      return {
        ...prompt,
        score: Math.min(98, base + features.length * 2 + briefBonus + retentionBonus + riskBonus),
      }
    })
    .sort((a, b) => b.score - a.score)
}

function normalizeStringArray(value, fallback) {
  if (!Array.isArray(value)) return fallback
  const cleaned = value.map((item) => String(item || '').trim()).filter(Boolean)
  return cleaned.length ? cleaned : fallback
}

function clampNumber(value, min, max, fallback) {
  const number = Number(value)
  if (!Number.isFinite(number)) return fallback
  return Math.min(max, Math.max(min, number))
}

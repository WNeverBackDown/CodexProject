import { access, readFile } from 'node:fs/promises'
import { normalizeAgentRun, runLocalWorkflow } from '../src/workflow.js'

const requiredFiles = [
  'index.html',
  'src/app.js',
  'src/data.js',
  'src/workflow.js',
  'src/App.css',
  'scripts/serve.mjs',
  'docs/ARCHITECTURE.md',
]

for (const file of requiredFiles) {
  await access(new URL(`../${file}`, import.meta.url))
}

const html = await readFile(new URL('../index.html', import.meta.url), 'utf8')
if (!html.includes('src/app.js') || !html.includes('src/App.css')) {
  throw new Error('index.html is not wired to the app assets')
}

const localRun = runLocalWorkflow('面向母婴电商，找到复购意向人群，要求 AUC 提升并生成 MR。', '电商增长')
if (localRun.features.length < 4 || localRun.candidatePrompts.length < 4 || localRun.submission.auc < 0.8) {
  throw new Error('local workflow smoke test failed')
}

const normalized = normalizeAgentRun({
  candidatePrompts: [{ title: '测试候选', score: 88, tactic: '测试策略' }],
  selectedPrompt: { title: '测试候选', score: 88, tactic: '测试策略' },
  submission: { auc: 0.83 },
})
if (!normalized.selectedPrompt.title || normalized.submission.auc !== 0.83) {
  throw new Error('normalizer smoke test failed')
}

console.log('Static app check passed.')

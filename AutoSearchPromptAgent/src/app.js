import {
  agentNodes,
  chartPoints,
  deepseekModels,
  heroFacts,
  kpis,
  markets,
  metrics,
  painPoints,
  principles,
} from './data.js'
import { runLocalWorkflow } from './workflow.js'

const state = {
  apiKey: sessionStorage.getItem('deepseek_api_key') || '',
  brief: '面向母婴电商，找到近期有复购意向但对价格敏感的人群，要求 AUC 稳定提升并自动生成可审查 MR。',
  market: markets[0],
  model: deepseekModels[0][0],
  activeNode: 'feature_extractor',
  loading: false,
  error: '',
  run: null,
}

const root = document.querySelector('#root')
render()

function currentRun() {
  return state.run || runLocalWorkflow(state.brief, state.market)
}

function render() {
  const run = currentRun()
  root.innerHTML = `
    <main>
      ${heroSection()}
      ${problemSection()}
      ${workflowSection()}
      ${agentConsole(run)}
      ${resultSection(run)}
      ${valueSection()}
    </main>
  `
  bindEvents()
}

function heroSection() {
  return `
    <section class="section hero-section">
      <div class="section-inner hero-grid">
        <div class="hero-copy">
          <p class="small-label">AUTOSEARCH PROMPT AGENT</p>
          <h1>人群挖掘 Agent</h1>
          <p class="lead">让人群挖掘从人工试错，变成自动迭代的生产闭环。</p>
        </div>
        <div class="author">作者：等待 / 自然</div>
        <div class="hero-cards">${heroFacts.map(([title, body, accent]) => infoCard(title, body, accent)).join('')}</div>
        <div class="kpi-grid">
          ${kpis.map(([label, value, note]) => `<article class="kpi-card"><span>${label}</span><strong>${value}</strong><p>${note}</p></article>`).join('')}
        </div>
      </div>
    </section>
  `
}

function problemSection() {
  return `
    <section class="section">
      <div class="section-inner">
        <p class="small-label">PROBLEM</p>
        <h2>业务真正的痛点不是“写一个分类器”，而是高迭代成本和迁移成本</h2>
        <div class="card-row danger-row">${painPoints.map(([title, body]) => infoCard(title, body, 'red')).join('')}</div>
        <h2 class="statement">所以我们做的不是单点模型，而是一套可自我迭代、可迁移复用的 Agent 工作流。</h2>
        <div class="card-row success-row">${principles.map(([title, body]) => infoCard(title, body, 'green')).join('')}</div>
      </div>
    </section>
  `
}

function workflowSection() {
  return `
    <section class="section">
      <div class="section-inner">
        <p class="small-label">SOLUTION</p>
        <h2>Agent 设计：从特征抽取到自动提交的完整闭环</h2>
        <div class="node-grid">
          ${agentNodes
            .map(
              ([id, title, label, description]) => `
                <button class="node-card ${state.activeNode === id ? 'is-active' : ''}" type="button" data-node="${id}">
                  <span>${title}</span><strong>${label}</strong><p>${description}</p>
                </button>
              `,
            )
            .join('')}
        </div>
        ${architectureDiagram()}
      </div>
    </section>
  `
}

function agentConsole(run) {
  const selectedNode = agentNodes.find(([id]) => id === state.activeNode) || agentNodes[0]
  const sourceText = run.source === 'deepseek' ? 'DeepSeek 真实运行结果' : '本地规则预估'
  const statusClass = run.source === 'deepseek' ? 'is-live' : 'is-local'

  return `
    <section class="section demo-section">
      <div class="section-inner">
        <p class="small-label">DEMO STORY</p>
        <h2>现场演示 Agent 运行</h2>
        <div class="api-card">
          <div class="panel-title">${icon('spark')}<strong>DeepSeek 接入</strong><span class="status-pill ${statusClass}">${sourceText}</span></div>
          <p class="api-note">API key 只发送到本机 Node 服务，由本机服务请求 DeepSeek；不会写入系统环境变量，也不会保存到项目文件。</p>
          <div class="inline-fields">
            <label>DeepSeek API key
              <input id="api-key" type="password" autocomplete="off" placeholder="sk-..." value="${escapeHtml(state.apiKey)}" />
            </label>
            <label>模型
              <select id="model">${deepseekModels.map(([value, label]) => `<option value="${value}" ${value === state.model ? 'selected' : ''}>${label}</option>`).join('')}</select>
            </label>
          </div>
          ${state.error ? `<div class="error-banner">${escapeHtml(state.error)}</div>` : ''}
        </div>
        <div class="console-grid">
          <div class="control-panel">
            <div class="panel-title">${icon('bot')}<strong>任务输入</strong></div>
            <label>业务场景
              <select id="market">${markets.map((item) => `<option ${item === state.market ? 'selected' : ''}>${item}</option>`).join('')}</select>
            </label>
            <label>需求描述
              <textarea id="brief">${escapeHtml(state.brief)}</textarea>
            </label>
            <button class="primary-action" type="button" id="run-button" ${state.loading ? 'disabled' : ''}>
              ${icon('play')}${state.loading ? 'DeepSeek 运行中...' : '调用 DeepSeek 运行 Agent'}
            </button>
            <button class="secondary-action" type="button" id="local-button">仅运行本地预估</button>
          </div>
          <div class="run-panel">
            <div class="panel-title">${icon('activity')}<strong>${selectedNode[2]}</strong><span>${selectedNode[1]}</span></div>
            <div class="model-output">
              <strong>本轮摘要</strong>
              <p>${escapeHtml(run.summary)}</p>
              ${run.usage ? `<small>tokens: prompt ${run.usage.prompt_tokens || 0} / completion ${run.usage.completion_tokens || 0} / total ${run.usage.total_tokens || 0}</small>` : ''}
            </div>
            <div class="feature-list">${run.features.map((feature) => `<span>${escapeHtml(feature)}</span>`).join('')}</div>
            <div class="prompt-list">
              ${run.candidatePrompts
                .map(
                  (prompt) => `
                    <article class="${prompt.id === run.selectedPrompt.id ? 'selected-prompt' : ''}">
                      <div>
                        <strong>${escapeHtml(prompt.title)}</strong>
                        <p>${escapeHtml(prompt.tactic)}</p>
                        ${prompt.prompt ? `<small>${escapeHtml(prompt.prompt)}</small>` : `<small>${escapeHtml(prompt.source)}</small>`}
                      </div>
                      <b>${Math.round(prompt.score)}</b>
                    </article>
                  `,
                )
                .join('')}
            </div>
          </div>
          <div class="judge-panel">
            <div class="panel-title">${icon('shield')}<strong>Judge 输出</strong></div>
            ${run.judgeFindings.map((finding) => `<div class="finding">${icon('check')}<p>${escapeHtml(finding)}</p></div>`).join('')}
            <div class="submission-card">
              ${icon('git')}
              <div>
                <strong>${escapeHtml(run.submission.title)}</strong>
                <p>AUC ${run.submission.auc} · precision ${run.evaluation.precision} · recall ${run.evaluation.recall}</p>
                <p>成本 ${run.submission.tokenCost} 元 · ${run.submission.elapsedHours} 小时 · 置信度 ${Math.round(run.submission.confidence)}%</p>
              </div>
            </div>
            <div class="mr-list">
              <strong>MR 草案</strong>
              ${run.submission.mrBody.map((item) => `<p>${escapeHtml(item)}</p>`).join('')}
            </div>
          </div>
        </div>
      </div>
    </section>
  `
}

function resultSection(run) {
  return `
    <section class="section">
      <div class="section-inner">
        <p class="small-label">RESULT</p>
        <h2>离线指标证明：Agent 能稳定找到更优解</h2>
        <div class="chart-panel">${aucChart(run.submission.auc)}</div>
        <div class="metric-table">
          <div class="metric-head"><span>指标</span><span>当前基线</span><span>Agent 结果</span><span>收益</span></div>
          ${metrics.map(([name, baseline, agent, delta]) => `<div class="metric-row"><span>${name}</span><span>${baseline}</span><span>${name === '结果准确性' ? `AUC ${run.submission.auc}` : agent}</span><strong>${delta}</strong></div>`).join('')}
        </div>
      </div>
    </section>
  `
}

function valueSection() {
  const items = [
    ['可复用', '不只适用于单一业务，可以迁移到任意需要从 Prompt 驱动的人群场景。'],
    ['节省人力成本', '用每日约 50 元 token 成本替代大量人工试错和评估成本。'],
    ['可控', 'Judge 只在指标达标时放行 MR，并保留溯源、灰度和回滚信息。'],
    ['已落地', '已接入生产节奏，上手快，后续维护成本低。'],
  ]
  return `
    <section class="section value-section">
      <div class="section-inner">
        <p class="small-label">VALUE</p>
        <h2>这个作品的价值</h2>
        <div class="value-grid">
          ${items.map(([title, body], index) => `<article class="value-card"><span>${String.fromCharCode(65 + index)}</span><strong>${title}</strong><p>${body}</p></article>`).join('')}
        </div>
        <h3>其他亮点</h3>
        <div class="highlight-row">
          <p>提供了一种 prompt data-kg 的使用方式。</p>
          <p>提供了一种在生产系统上可持续迭代 prompt 的方法。</p>
          <p>提供了一种让 ReRanker 与业务指标共同演进的闭环。</p>
        </div>
      </div>
    </section>
  `
}

function architectureDiagram() {
  return `
    <div class="architecture-panel">
      <div class="pipeline">
        ${agentNodes
          .map(
            ([id, , label], index) => `
              <div class="pipeline-node ${state.activeNode === id ? 'is-active' : ''}">
                ${icon(['brain', 'search', 'spark', 'target', 'badge', 'git'][index])}<strong>${label}</strong>
                ${index < agentNodes.length - 1 ? '<span class="pipeline-arrow">→</span>' : ''}
              </div>
            `,
          )
          .join('')}
      </div>
      <div class="system-map">
        ${[
          ['layers', '需求 / 样本 / 历史指标', '统一成任务上下文，进入特征抽取。'],
          ['blocks', 'Prompt 资产库', '模板、成功案例、失败样本、业务词表。'],
          ['bot', 'Agent Runtime', '调用 DeepSeek 生成候选、解释和评估。'],
          ['shield', 'Judge Gate', '阈值、风控、解释、回滚条件。'],
          ['file', 'MR / 评估报告', '提交 Prompt、指标和上线说明。'],
        ]
          .map(([iconName, title, body]) => `<div class="map-box">${icon(iconName)}<strong>${title}</strong><p>${body}</p></div>`)
          .join('')}
      </div>
    </div>
  `
}

function aucChart(currentAuc) {
  const width = 880
  const height = 270
  const padding = 34
  const values = [...chartPoints.slice(0, -1), currentAuc]
  const min = 0.68
  const max = 0.84
  const coords = values.map((value, index) => {
    const x = padding + (index / (values.length - 1)) * (width - padding * 2)
    const y = height - padding - ((value - min) / (max - min)) * (height - padding * 2)
    return [x, y]
  })
  const path = coords.map(([x, y], index) => `${index === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`).join(' ')
  return `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="AUC by log date">
      <rect width="${width}" height="${height}" rx="8" fill="#ffffff"></rect>
      ${[0.7, 0.74, 0.78, 0.82]
        .map((tick) => {
          const y = height - padding - ((tick - min) / (max - min)) * (height - padding * 2)
          return `<g><line x1="${padding}" x2="${width - padding}" y1="${y}" y2="${y}" stroke="#edf1f7"></line><text x="10" y="${y + 4}" fill="#8390a5" font-size="11">${tick.toFixed(2)}</text></g>`
        })
        .join('')}
      <path d="${path}" fill="none" stroke="#3174ff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></path>
      ${coords.map(([x, y], index) => `<circle cx="${x}" cy="${y}" r="${index === coords.length - 1 ? 6 : 3.5}" fill="${index === coords.length - 1 ? '#21b56b' : '#3174ff'}"></circle>`).join('')}
      <text x="${width / 2 - 110}" y="24" fill="#1b2a4a" font-size="14" font-weight="700">ai.search_llm_eval_could_ci AUC by log_date</text>
      <text x="${width - 170}" y="55" fill="#1b8d54" font-size="12" font-weight="700">max ${Number(currentAuc).toFixed(3)}</text>
    </svg>
  `
}

function bindEvents() {
  document.querySelectorAll('[data-node]').forEach((button) => {
    button.addEventListener('click', () => {
      state.activeNode = button.dataset.node
      render()
    })
  })

  document.querySelector('#market').addEventListener('change', (event) => {
    state.market = event.target.value
    state.run = null
    render()
  })

  document.querySelector('#model').addEventListener('change', (event) => {
    state.model = event.target.value
  })

  document.querySelector('#api-key').addEventListener('input', (event) => {
    state.apiKey = event.target.value.trim()
    if (state.apiKey) sessionStorage.setItem('deepseek_api_key', state.apiKey)
    else sessionStorage.removeItem('deepseek_api_key')
  })

  document.querySelector('#brief').addEventListener('input', (event) => {
    state.brief = event.target.value
  })

  document.querySelector('#local-button').addEventListener('click', () => {
    state.error = ''
    state.run = runLocalWorkflow(state.brief, state.market)
    render()
  })

  document.querySelector('#run-button').addEventListener('click', runDeepSeekAgent)
}

async function runDeepSeekAgent() {
  state.loading = true
  state.error = ''
  render()

  try {
    const response = await fetch('/api/run-agent', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        apiKey: state.apiKey,
        model: state.model,
        brief: state.brief,
        market: state.market,
      }),
    })
    const payload = await response.json()
    if (!response.ok) {
      state.error = payload.error || 'Agent 运行失败。'
      state.run = payload.fallback || runLocalWorkflow(state.brief, state.market)
      return
    }
    state.run = payload.run
  } catch (error) {
    state.error = `本地服务请求失败：${error.message}`
    state.run = runLocalWorkflow(state.brief, state.market)
  } finally {
    state.loading = false
    render()
  }
}

function infoCard(title, body, accent) {
  return `<article class="info-card accent-${accent}"><strong>${escapeHtml(title)}</strong><p>${escapeHtml(body)}</p></article>`
}

function icon(name) {
  const paths = {
    bot: '<rect x="5" y="9" width="14" height="10" rx="3"/><path d="M12 5v4M8 14h.01M16 14h.01"/>',
    play: '<path d="M8 5v14l11-7z" fill="currentColor"/>',
    activity: '<path d="M3 12h4l3-8 4 16 3-8h4"/>',
    shield: '<path d="M12 3 20 6v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/>',
    check: '<path d="m5 12 4 4L19 6"/>',
    git: '<path d="M7 7h10v10H7z"/><path d="M7 12H3m18 0h-4M12 7V3m0 18v-4"/>',
    brain: '<path d="M9 4a4 4 0 0 0-4 4v8a4 4 0 0 0 4 4M15 4a4 4 0 0 1 4 4v8a4 4 0 0 1-4 4M9 8h6M9 12h6M9 16h6"/>',
    search: '<circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/>',
    spark: '<path d="M12 3l2 6 6 2-6 2-2 6-2-6-6-2 6-2 2-6z"/>',
    target: '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/>',
    badge: '<path d="M7 4h10l3 6-8 10-8-10 3-6z"/><path d="m9 11 2 2 4-4"/>',
    layers: '<path d="m12 3 9 5-9 5-9-5 9-5z"/><path d="m3 12 9 5 9-5M3 16l9 5 9-5"/>',
    blocks: '<rect x="4" y="4" width="6" height="6"/><rect x="14" y="4" width="6" height="6"/><rect x="9" y="14" width="6" height="6"/>',
    file: '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
  }
  return `<svg class="icon-svg" viewBox="0 0 24 24" aria-hidden="true">${paths[name] || paths.spark}</svg>`
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')
}

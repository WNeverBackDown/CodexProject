import { createServer } from 'node:http'
import { createReadStream } from 'node:fs'
import { stat } from 'node:fs/promises'
import { extname, join, normalize } from 'node:path'
import { fileURLToPath } from 'node:url'
import { normalizeAgentRun, promptBank, runLocalWorkflow } from '../src/workflow.js'

const root = fileURLToPath(new URL('..', import.meta.url))
const startPort = Number(process.env.PORT || 4173)
const deepseekEndpoint = 'https://api.deepseek.com/chat/completions'
const types = new Map([
  ['.html', 'text/html; charset=utf-8'],
  ['.css', 'text/css; charset=utf-8'],
  ['.js', 'text/javascript; charset=utf-8'],
  ['.svg', 'image/svg+xml'],
  ['.png', 'image/png'],
])

const server = createServer(async (request, response) => {
  try {
    if (request.method === 'POST' && request.url === '/api/run-agent') {
      await handleAgentRun(request, response)
      return
    }

    if (request.method === 'GET' && request.url === '/api/health') {
      sendJson(response, 200, { ok: true })
      return
    }

    await serveStatic(request, response)
  } catch (error) {
    sendJson(response, 500, { error: error.message || 'Server error' })
  }
})

listen(startPort)

async function handleAgentRun(request, response) {
  const body = await readJson(request)
  const apiKey = String(body.apiKey || '').trim()
  const brief = String(body.brief || '').trim()
  const market = String(body.market || '通用业务').trim()
  const model = String(body.model || 'deepseek-v4-flash').trim()

  if (!apiKey) {
    sendJson(response, 400, { error: '请先填写 DeepSeek API key。' })
    return
  }

  if (!brief) {
    sendJson(response, 400, { error: '请先填写业务需求。' })
    return
  }

  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), 60000)

  try {
    const apiResponse = await fetch(deepseekEndpoint, {
      method: 'POST',
      signal: controller.signal,
      headers: {
        'content-type': 'application/json',
        authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model,
        messages: buildMessages({ brief, market }),
        response_format: { type: 'json_object' },
        temperature: 0.2,
        stream: false,
      }),
    })

    const payload = await apiResponse.json().catch(() => ({}))

    if (!apiResponse.ok) {
      const message = payload?.error?.message || `DeepSeek API 请求失败：HTTP ${apiResponse.status}`
      sendJson(response, apiResponse.status, { error: message })
      return
    }

    const content = payload?.choices?.[0]?.message?.content
    if (!content) {
      sendJson(response, 502, { error: 'DeepSeek 没有返回可解析内容。' })
      return
    }

    const parsed = parseModelJson(content)
    const normalized = normalizeAgentRun({
      ...parsed,
      source: 'deepseek',
      usage: payload.usage || null,
      rawModelText: content,
    })

    sendJson(response, 200, { run: normalized })
  } catch (error) {
    const fallback = runLocalWorkflow(brief, market)
    const message = error.name === 'AbortError' ? 'DeepSeek 请求超时，已返回本地兜底结果。' : `DeepSeek 请求失败：${error.message}`
    sendJson(response, 502, { error: message, fallback })
  } finally {
    clearTimeout(timer)
  }
}

function buildMessages({ brief, market }) {
  return [
    {
      role: 'system',
      content: [
        '你是一个生产级 AutoSearch Prompt Agent。',
        '你要根据业务需求完成人群挖掘方案设计，而不是复述页面文案。',
        '必须只输出合法 JSON，不要输出 Markdown。',
        'JSON 字段必须包含：summary, features, candidatePrompts, selectedPrompt, evaluation, judgeFindings, submission。',
        'candidatePrompts 至少 4 个，每个包含 id, title, score, source, tactic, prompt。',
        'evaluation 包含 auc, precision, recall, riskLevel, notes。',
        'submission 包含 title, confidence, auc, tokenCost, elapsedHours, mrBody。',
        '所有解释、Prompt 和 MR 内容使用中文。',
      ].join('\n'),
    },
    {
      role: 'user',
      content: JSON.stringify(
        {
          task: '为业务需求生成可落地的人群挖掘 Agent 运行结果。',
          market,
          brief,
          baseline: {
            humanCost: '3 人日',
            baselineAuc: 0.76,
            targetAuc: 0.82,
            dailyTokenBudgetCny: 50,
          },
          promptAssets: promptBank,
          outputContract: {
            summary: '一句话说明本轮 Agent 做了什么',
            features: ['结构化人群特征'],
            candidatePrompts: [{ id: 'string', title: 'string', score: 0, source: 'string', tactic: 'string', prompt: 'string' }],
            selectedPrompt: { id: 'string', title: 'string', score: 0, source: 'string', tactic: 'string', prompt: 'string' },
            evaluation: { auc: 0.82, precision: 0.78, recall: 0.76, riskLevel: 'low|medium|high', notes: ['string'] },
            judgeFindings: ['上线判断、成本判断、风险判断'],
            submission: {
              title: 'MR 标题',
              confidence: 88,
              auc: 0.82,
              tokenCost: 50,
              elapsedHours: 3,
              mrBody: ['MR 描述要点'],
            },
          },
        },
        null,
        2,
      ),
    },
  ]
}

async function serveStatic(request, response) {
  const url = new URL(request.url || '/', `http://${request.headers.host}`)
  const requestedPath = url.pathname === '/' ? '/index.html' : url.pathname
  const cleanPath = normalize(decodeURIComponent(requestedPath)).replace(/^(\.\.[/\\])+/, '')
  const requested = cleanPath.replace(/^[/\\]/, '')
  const filePath = join(root, requested)

  if (!filePath.startsWith(root)) {
    response.writeHead(403)
    response.end('Forbidden')
    return
  }

  try {
    const info = await stat(filePath)
    if (!info.isFile()) throw new Error('Not a file')
    response.writeHead(200, { 'content-type': types.get(extname(filePath)) || 'application/octet-stream' })
    createReadStream(filePath).pipe(response)
  } catch {
    response.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' })
    response.end('Not found')
  }
}

function parseModelJson(content) {
  try {
    return JSON.parse(content)
  } catch {
    const match = content.match(/\{[\s\S]*\}/)
    if (!match) throw new Error('DeepSeek 返回内容不是 JSON。')
    return JSON.parse(match[0])
  }
}

async function readJson(request) {
  const chunks = []
  for await (const chunk of request) {
    chunks.push(chunk)
  }
  const raw = Buffer.concat(chunks).toString('utf8')
  if (!raw) return {}
  return JSON.parse(raw)
}

function sendJson(response, statusCode, payload) {
  response.writeHead(statusCode, { 'content-type': 'application/json; charset=utf-8' })
  response.end(JSON.stringify(payload))
}

function listen(port, attempts = 0) {
  server.once('error', (error) => {
    if (error.code === 'EADDRINUSE' && attempts < 10) {
      listen(port + 1, attempts + 1)
      return
    }
    throw error
  })

  server.listen(port, '127.0.0.1', () => {
    console.log(`AutoSearch Prompt Agent running at http://127.0.0.1:${port}`)
  })
}

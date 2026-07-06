import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 45000,
})

api.interceptors.request.use((config) => {
  const token = window.Clerk?.session?.lastActiveToken?.getRawString?.()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export async function translateSign(landmarks, language = 'en', sessionId = '') {
  const { data } = await api.post('/translate', {
    landmarks,
    language,
    session_id: sessionId,
  })
  return data
}

export async function speakText(text, language = 'en') {
  const { data } = await api.post('/tts', { text, language })
  return data
}

export async function logEvent(eventType, metadata = {}, sessionId = '') {
  const { data } = await api.post('/analytics', {
    event_type: eventType,
    metadata,
    session_id: sessionId,
  })
  return data
}

export async function executeMCPTool(toolName, toolArgs = {}, confirmed = false, sessionId = '') {
  const { data } = await api.post('/mcp/execute', {
    tool_name: toolName,
    tool_args: toolArgs,
    confirmed,
    session_id: sessionId,
  })
  return data
}

export default api

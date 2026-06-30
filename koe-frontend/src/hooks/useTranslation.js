import { useState, useRef, useCallback } from 'react'
import { translateSign } from '../services/api'

export default function useTranslation(language = 'en', sessionId = '') {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const lastSentRef = useRef(0)
  const debounceRef = useRef(null)

  const translate = useCallback((landmarks, onResult) => {
    if (!landmarks || landmarks.length === 0) return

    const now = Date.now()
    if (now - lastSentRef.current < 1000) return

    if (debounceRef.current) clearTimeout(debounceRef.current)

    debounceRef.current = setTimeout(async () => {
      lastSentRef.current = Date.now()
      setLoading(true)
      setError(null)
      try {
        const formatted = landmarks.map((hand) =>
          hand.map((p) => ({ x: p.x, y: p.y, z: p.z }))
        )
        const data = await translateSign(formatted, language, sessionId)
        onResult?.(data)
      } catch (err) {
        setError(err.message || 'Translation failed')
      } finally {
        setLoading(false)
      }
    }, 300)
  }, [language, sessionId])

  return { loading, error, translate }
}

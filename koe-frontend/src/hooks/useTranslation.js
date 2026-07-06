import { useState, useRef, useCallback } from 'react'
import { translateSign } from '../services/api'

const COOLDOWN_MS = 4000

export default function useTranslation(language = 'en', sessionId = '') {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const lastSentRef = useRef(0)
  const lastLabelRef = useRef(null)
  const debounceRef = useRef(null)

  const translate = useCallback((landmarks, onResult) => {
    if (!landmarks || landmarks.length === 0) return

    const now = Date.now()
    if (now - lastSentRef.current < COOLDOWN_MS) return

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
        if (data?.sign_label && data.sign_label === lastLabelRef.current) return
        lastLabelRef.current = data?.sign_label || null
        onResult?.(data)
      } catch (err) {
        setError(err.message || 'Translation failed')
      } finally {
        setLoading(false)
      }
    }, 500)
  }, [language, sessionId])

  return { loading, error, translate }
}

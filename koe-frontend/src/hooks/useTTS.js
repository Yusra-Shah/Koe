import { useRef, useState, useCallback } from 'react'
import { speakText } from '../services/api'

export default function useTTS() {
  const [speaking, setSpeaking] = useState(false)
  const audioRef = useRef(null)

  const speak = useCallback(async (text, language = 'en') => {
    if (!text || speaking) return

    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }

    setSpeaking(true)
    try {
      const data = await speakText(text, language)

      if (data.audio_base64) {
        const binary = atob(data.audio_base64)
        const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0))
        const blob = new Blob([bytes], { type: 'audio/mp3' })
        const url = URL.createObjectURL(blob)
        const audio = new Audio(url)
        audioRef.current = audio
        audio.onended = () => {
          setSpeaking(false)
          URL.revokeObjectURL(url)
        }
        audio.onerror = () => setSpeaking(false)
        await audio.play()
      } else {
        // Fallback to browser TTS when backend TTS is unavailable
        if ('speechSynthesis' in window) {
          const utterance = new SpeechSynthesisUtterance(text)
          utterance.lang = language === 'ur' ? 'ur-PK' : 'en-US'
          utterance.rate = 0.9
          utterance.onend = () => setSpeaking(false)
          utterance.onerror = () => setSpeaking(false)
          window.speechSynthesis.speak(utterance)
        } else {
          setSpeaking(false)
        }
      }
    } catch {
      // Backend TTS failed — fall back to browser TTS
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text)
        utterance.lang = language === 'ur' ? 'ur-PK' : 'en-US'
        utterance.rate = 0.9
        utterance.onend = () => setSpeaking(false)
        utterance.onerror = () => setSpeaking(false)
        window.speechSynthesis.speak(utterance)
      } else {
        setSpeaking(false)
      }
    }
  }, [speaking])

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }
    window.speechSynthesis?.cancel()
    setSpeaking(false)
  }, [])

  return { speak, stop, speaking }
}

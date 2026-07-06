import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import useTTS from '../hooks/useTTS'

export default function ReverseMode({ language, onClose }) {
  const [inputText, setInputText] = useState('')
  const [displayText, setDisplayText] = useState('')
  const { speak, speaking } = useTTS()

  const handleSpeak = async () => {
    if (!inputText.trim()) return
    setDisplayText(inputText.trim())
    await speak(inputText.trim(), language)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSpeak()
    }
  }

  const handleClear = () => {
    setInputText('')
    setDisplayText('')
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 16 }}
      transition={{ duration: 0.25 }}
      className="bg-white border border-koe-border rounded-koe-lg p-5 flex flex-col gap-4"
    >
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-koe-stone font-medium text-sm">Reverse Mode</h3>
          <p className="text-koe-stone-muted text-xs mt-0.5">
            Hearing person types, deaf user reads
          </p>
        </div>
        <button
          onClick={onClose}
          className="w-7 h-7 rounded-full flex items-center justify-center hover:bg-koe-amber-light transition-colors duration-200"
          aria-label="Close reverse mode"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#78716C" strokeWidth="2.5" strokeLinecap="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      {displayText && (
        <div className="bg-koe-amber-pale rounded-koe-lg p-4 min-h-[80px] flex items-center justify-center">
          <p
            className="text-koe-stone text-2xl font-medium text-center leading-relaxed"
            dir={language === 'ur' ? 'rtl' : 'ltr'}
          >
            {displayText}
          </p>
        </div>
      )}

      <div className="flex gap-2">
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={language === 'ur' ? 'یہاں ٹائپ کریں...' : 'Type here and press Enter or Speak...'}
          rows={2}
          dir={language === 'ur' ? 'rtl' : 'ltr'}
          className="flex-1 resize-none rounded-koe-md border border-koe-border px-3 py-2 text-sm text-koe-stone placeholder:text-koe-stone-muted focus:outline-none focus:border-koe-amber bg-koe-cream transition-colors duration-200"
        />
        <div className="flex flex-col gap-2">
          <button
            onClick={handleSpeak}
            disabled={speaking || !inputText.trim()}
            className="px-3 py-2 bg-koe-amber text-white rounded-koe-md text-sm font-medium hover:opacity-90 disabled:opacity-50 transition-all duration-200 whitespace-nowrap"
          >
            {speaking ? '...' : 'Speak'}
          </button>
          {displayText && (
            <button
              onClick={handleClear}
              className="px-3 py-2 bg-koe-amber-light text-koe-amber rounded-koe-md text-sm font-medium hover:bg-koe-amber-pale transition-all duration-200"
            >
              Clear
            </button>
          )}
        </div>
      </div>
    </motion.div>
  )
}

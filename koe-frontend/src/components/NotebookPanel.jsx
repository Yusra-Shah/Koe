import { motion, AnimatePresence } from 'framer-motion'
import ConfidenceRing from './ConfidenceRing'
import useTTS from '../hooks/useTTS'

function NotebookEntry({ entry, language }) {
  const { speak, speaking } = useTTS()
  const displayText = language === 'ur' && entry.text_ur ? entry.text_ur : entry.text_en

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
      className="flex items-start gap-3 py-3 border-b border-koe-border last:border-0"
    >
      <ConfidenceRing confidence={entry.confidence} size={48} />
      <div className="flex-1 min-w-0">
        <p className="text-koe-stone text-base leading-relaxed break-words">{displayText}</p>
        <div className="flex items-center gap-2 mt-1">
          <span className="text-koe-stone-muted text-xs">{entry.sign_label}</span>
          {entry.mcp_intent && (
            <span className="px-1.5 py-0.5 rounded-full bg-koe-sky text-koe-stone text-xs">
              {entry.mcp_intent.replace('_', ' ')}
            </span>
          )}
          <span className="text-koe-stone-muted text-xs ml-auto">
            {new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
      </div>
      <button
        onClick={() => speak(displayText, language)}
        disabled={speaking}
        aria-label="Read aloud"
        className="shrink-0 w-8 h-8 rounded-full flex items-center justify-center hover:bg-koe-amber-light transition-colors duration-200 disabled:opacity-50"
      >
        {speaking ? (
          <motion.div
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ repeat: Infinity, duration: 0.8 }}
            className="w-3 h-3 rounded-full bg-koe-amber"
          />
        ) : (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#B45309" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
            <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
            <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
          </svg>
        )}
      </button>
    </motion.div>
  )
}

export default function NotebookPanel({ entries, language, onClear }) {
  return (
    <div className="flex flex-col h-full bg-white border border-koe-border rounded-koe-lg overflow-hidden">
      <div className="flex items-center justify-between px-5 py-3 border-b border-koe-border">
        <h2 className="font-display text-lg text-koe-amber">Koe Notebook</h2>
        {entries.length > 0 && (
          <button
            onClick={onClear}
            className="text-xs text-koe-stone-muted hover:text-koe-stone transition-colors duration-200"
          >
            Clear
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto px-5">
        <AnimatePresence mode="popLayout">
          {entries.length === 0 ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center h-40 gap-2"
            >
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#E7E5E4" strokeWidth="1.5">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
              </svg>
              <p className="text-koe-stone-muted text-sm text-center">
                Start signing to see<br />translations here.
              </p>
            </motion.div>
          ) : (
            entries.map((entry) => (
              <NotebookEntry key={entry.id} entry={entry} language={language} />
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

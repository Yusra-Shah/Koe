import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { executeMCPTool } from '../services/api'

const TOOL_META = {
  emergency_contact: {
    label: 'Send Emergency Message',
    description: 'This will send an emergency contact message on your behalf.',
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#B45309" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.5 2 2 0 0 1 3.59 1.3h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.4a16 16 0 0 0 5.69 5.69l.92-.92a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 21.22 16z" />
      </svg>
    ),
  },
  form_fill: {
    label: 'Submit Form',
    description: 'This will fill and submit a form on your behalf.',
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#B45309" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
      </svg>
    ),
  },
  appointment_request: {
    label: 'Request Appointment',
    description: 'This will send an appointment request on your behalf.',
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#B45309" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
        <line x1="16" y1="2" x2="16" y2="6" />
        <line x1="8" y1="2" x2="8" y2="6" />
        <line x1="3" y1="10" x2="21" y2="10" />
      </svg>
    ),
  },
}

export default function MCPConfirmDialog({ intent, translatedText, sessionId, onClose }) {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const meta = TOOL_META[intent]

  if (!meta) return null

  const handleConfirm = async () => {
    setLoading(true)
    try {
      const data = await executeMCPTool(
        intent,
        { message: translatedText },
        true,
        sessionId,
      )
      setResult({ success: true, message: data.message })
    } catch {
      setResult({ success: false, message: 'Action could not be completed. Please try again.' })
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async () => {
    try {
      await executeMCPTool(intent, {}, false, sessionId)
    } catch {
      // Fire-and-forget — just logging the cancellation
    }
    onClose()
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-koe-stone/40 backdrop-blur-sm"
        onClick={(e) => { if (e.target === e.currentTarget && !loading) onClose() }}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 8 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 8 }}
          transition={{ duration: 0.25, ease: [0.25, 0.1, 0.25, 1] }}
          className="bg-white rounded-koe-xl shadow-xl max-w-sm w-full p-6"
        >
          {result ? (
            <div className="text-center">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 ${result.success ? 'bg-koe-sage' : 'bg-koe-sakura'}`}>
                {result.success ? (
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                ) : (
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#DC2626" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                )}
              </div>
              <p className="text-koe-stone font-medium mb-1">{result.success ? 'Done' : 'Could not complete'}</p>
              <p className="text-koe-stone-muted text-sm mb-5">{result.message}</p>
              <button
                onClick={onClose}
                className="w-full py-2.5 bg-koe-amber text-white rounded-koe-md text-sm font-medium hover:opacity-90 transition-all duration-200"
              >
                Close
              </button>
            </div>
          ) : (
            <>
              <div className="flex items-start gap-4 mb-5">
                <div className="w-12 h-12 rounded-full bg-koe-amber-light flex items-center justify-center shrink-0">
                  {meta.icon}
                </div>
                <div>
                  <h3 className="text-koe-stone font-medium text-base">{meta.label}</h3>
                  <p className="text-koe-stone-muted text-sm mt-0.5">{meta.description}</p>
                </div>
              </div>

              {translatedText && (
                <div className="bg-koe-amber-pale rounded-koe-lg px-4 py-3 mb-5">
                  <p className="text-koe-stone-muted text-xs mb-1">From your sign</p>
                  <p className="text-koe-stone text-sm leading-relaxed">"{translatedText}"</p>
                </div>
              )}

              <p className="text-koe-stone-muted text-xs text-center mb-5">
                Koe will take this action on your behalf. You can cancel at any time.
              </p>

              <div className="flex gap-3">
                <button
                  onClick={handleCancel}
                  disabled={loading}
                  className="flex-1 py-2.5 border border-koe-border text-koe-stone-muted rounded-koe-md text-sm font-medium hover:bg-koe-amber-pale transition-all duration-200 disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirm}
                  disabled={loading}
                  className="flex-1 py-2.5 bg-koe-amber text-white rounded-koe-md text-sm font-medium hover:opacity-90 transition-all duration-200 disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ repeat: Infinity, duration: 0.8, ease: 'linear' }}
                      className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                    />
                  ) : 'Confirm'}
                </button>
              </div>
            </>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

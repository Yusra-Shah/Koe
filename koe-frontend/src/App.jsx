import { ClerkProvider, SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/clerk-react'
import { useState, useCallback, useRef } from 'react'
import { AnimatePresence } from 'framer-motion'
import CameraView from './components/CameraView'
import NotebookPanel from './components/NotebookPanel'
import QuickCards from './components/QuickCards'
import ReverseMode from './components/ReverseMode'
import MCPConfirmDialog from './components/MCPConfirmDialog'
import useTranslation from './hooks/useTranslation'

const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY
let entryCounter = 0

function TranslationPanel() {
  const [language, setLanguage] = useState('en')
  const [entries, setEntries] = useState([])
  const [showReverse, setShowReverse] = useState(false)
  const [mcpPending, setMcpPending] = useState(null) // { intent, text }
  const sessionId = useRef(crypto.randomUUID())

  const { loading, translate } = useTranslation(language, sessionId.current)

  const handleLandmarks = useCallback((lm) => {
    translate(lm, (result) => {
      if (!result || result.repeat_requested) return
      if (result.mcp_intent) {
        setMcpPending({ intent: result.mcp_intent, text: result.text || result.text_en || '' })
      }
      setEntries((prev) => [
        {
          id: ++entryCounter,
          text_en: result.text || result.text_en || '',
          text_ur: result.text_ur || '',
          sign_label: result.sign_label || '',
          confidence: result.confidence || 0,
          mcp_intent: result.mcp_intent || null,
          timestamp: Date.now(),
        },
        ...prev,
      ].slice(0, 50))
    })
  }, [translate])

  return (
    <main className="flex-1 flex flex-col gap-4 p-4 lg:p-6 overflow-hidden">
      <div className="flex-1 flex flex-col lg:flex-row gap-4 min-h-0">
        {/* Left — Camera + controls */}
        <div className="flex flex-col gap-3 lg:flex-1">
          <CameraView onLandmarks={handleLandmarks} loading={loading} />

          {/* Language + Reverse Mode toggle */}
          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={() => setLanguage('en')}
              className={`px-3 py-1.5 rounded-koe-md text-sm font-medium transition-all duration-200 ${language === 'en' ? 'bg-koe-amber text-white' : 'bg-koe-amber-light text-koe-amber'}`}
            >
              English
            </button>
            <button
              onClick={() => setLanguage('ur')}
              className={`px-3 py-1.5 rounded-koe-md text-sm font-medium transition-all duration-200 ${language === 'ur' ? 'bg-koe-amber text-white' : 'bg-koe-amber-light text-koe-amber'}`}
            >
              اردو
            </button>
            <div className="flex-1" />
            <button
              onClick={() => setShowReverse((v) => !v)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-koe-md text-sm font-medium border transition-all duration-200 ${showReverse ? 'bg-koe-stone text-koe-cream border-koe-stone' : 'bg-white text-koe-stone-muted border-koe-border hover:border-koe-stone'}`}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z" />
              </svg>
              Reverse
            </button>
          </div>

          {/* Reverse Mode */}
          <AnimatePresence>
            {showReverse && (
              <ReverseMode
                language={language}
                onClose={() => setShowReverse(false)}
              />
            )}
          </AnimatePresence>

          {/* Quick Cards */}
          <QuickCards language={language} />
        </div>

        {/* MCP Confirmation Dialog */}
        <AnimatePresence>
          {mcpPending && (
            <MCPConfirmDialog
              intent={mcpPending.intent}
              translatedText={mcpPending.text}
              sessionId={sessionId.current}
              onClose={() => setMcpPending(null)}
            />
          )}
        </AnimatePresence>

        {/* Right — Notebook */}
        <div className="lg:w-80 flex flex-col min-h-[300px] lg:min-h-0">
          <NotebookPanel
            entries={entries}
            language={language}
            onClear={() => setEntries([])}
          />
        </div>
      </div>
    </main>
  )
}

function KoeApp() {
  return (
    <div className="flex flex-col min-h-svh bg-koe-cream">
      <header className="flex items-center justify-between px-6 py-4 border-b border-koe-border shrink-0">
        <h1 className="font-display text-3xl text-koe-amber font-medium tracking-tight">
          Koe
        </h1>
        <div className="flex items-center gap-4">
          <SignedIn>
            <UserButton />
          </SignedIn>
          <SignedOut>
            <SignInButton mode="modal">
              <button className="px-4 py-2 bg-koe-amber text-white rounded-koe-md text-sm font-medium hover:opacity-90 transition-all duration-200">
                Sign In
              </button>
            </SignInButton>
          </SignedOut>
        </div>
      </header>

      <SignedOut>
        <main className="flex-1 flex items-center justify-center p-6">
          <div className="text-center max-w-md">
            <h2 className="font-display text-5xl text-koe-amber mb-4">Koe</h2>
            <p className="text-koe-stone-muted text-lg mb-2">声 — Your Voice</p>
            <p className="text-koe-stone-muted text-sm leading-relaxed mb-6">
              AI-powered sign language communication for deaf, mute, and hard-of-hearing users.
              Sign in to begin.
            </p>
            <SignInButton mode="modal">
              <button className="px-6 py-3 bg-koe-amber text-white rounded-koe-md text-sm font-medium hover:opacity-90 transition-all duration-200">
                Sign In to Koe
              </button>
            </SignInButton>
          </div>
        </main>
      </SignedOut>

      <SignedIn>
        <TranslationPanel />
      </SignedIn>

      <footer className="shrink-0 text-center py-3 text-xs text-koe-stone-muted border-t border-koe-border">
        Koe — Inspired by A Silent Voice
      </footer>
    </div>
  )
}

function App() {
  if (!clerkPubKey) {
    return (
      <div className="flex flex-col min-h-svh bg-koe-cream items-center justify-center p-6">
        <h1 className="font-display text-5xl text-koe-amber mb-4">Koe</h1>
        <p className="text-koe-stone-muted text-sm">
          Set <code className="bg-koe-amber-light px-1 rounded text-koe-amber">VITE_CLERK_PUBLISHABLE_KEY</code> in .env to enable authentication.
        </p>
      </div>
    )
  }

  return (
    <ClerkProvider publishableKey={clerkPubKey}>
      <KoeApp />
    </ClerkProvider>
  )
}

export default App

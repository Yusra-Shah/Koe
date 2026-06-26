import { ClerkProvider, SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/clerk-react'
import { useState, useCallback } from 'react'
import CameraView from './components/CameraView'
import ConfidenceRing from './components/ConfidenceRing'
import useTranslation from './hooks/useTranslation'

const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

function TranslationPanel() {
  const [language, setLanguage] = useState('en')
  const { result, loading, translate } = useTranslation(language)

  const handleLandmarks = useCallback((lm) => {
    translate(lm)
  }, [translate])

  return (
    <main className="flex-1 flex flex-col lg:flex-row gap-6 p-6">
      <div className="flex-1 flex flex-col items-center gap-4">
        <CameraView onLandmarks={handleLandmarks} />

        <div className="flex items-center gap-3">
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
        </div>
      </div>

      <div className="lg:w-80 flex flex-col gap-4">
        <div className="bg-white border border-koe-border rounded-koe-lg p-5 min-h-[200px]">
          <h2 className="font-display text-lg text-koe-amber mb-3">Koe Notebook</h2>

          {result ? (
            <div className="flex items-start gap-3">
              <ConfidenceRing confidence={result.confidence} size={56} />
              <div className="flex-1">
                <p className="text-koe-stone text-base leading-relaxed">{result.text}</p>
                <p className="text-koe-stone-muted text-xs mt-1">
                  Sign: {result.sign_label} · {result.language === 'ur' ? 'اردو' : 'English'}
                </p>
              </div>
            </div>
          ) : (
            <p className="text-koe-stone-muted text-sm italic">
              {loading ? 'Translating...' : 'Start signing to see translations here.'}
            </p>
          )}
        </div>
      </div>
    </main>
  )
}

function KoeApp() {
  return (
    <div className="flex flex-col min-h-svh bg-koe-cream">
      <header className="flex items-center justify-between px-6 py-4 border-b border-koe-border">
        <h1 className="font-display text-3xl text-koe-amber font-medium tracking-tight">
          Koe
        </h1>
        <div className="flex items-center gap-4">
          <SignedIn>
            <UserButton />
          </SignedIn>
          <SignedOut>
            <SignInButton mode="modal">
              <button className="px-4 py-2 bg-koe-amber text-white rounded-koe-md text-sm font-medium transition-all duration-200 hover:opacity-90">
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
            <p className="text-koe-stone-muted text-lg mb-2">Your Voice</p>
            <p className="text-koe-stone-muted text-sm leading-relaxed">
              AI-powered sign language communication. Sign in to begin.
            </p>
          </div>
        </main>
      </SignedOut>

      <SignedIn>
        <TranslationPanel />
      </SignedIn>

      <footer className="text-center py-4 text-xs text-koe-stone-muted border-t border-koe-border">
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
          Set VITE_CLERK_PUBLISHABLE_KEY in .env to enable authentication.
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

import { ClerkProvider, SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/clerk-react'

const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

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

      <main className="flex-1 flex items-center justify-center p-6">
        <SignedOut>
          <div className="text-center max-w-md">
            <h2 className="font-display text-5xl text-koe-amber mb-4">Koe</h2>
            <p className="text-koe-stone-muted text-lg mb-2">Your Voice</p>
            <p className="text-koe-stone-muted text-sm leading-relaxed">
              AI-powered sign language communication. Sign in to begin.
            </p>
          </div>
        </SignedOut>

        <SignedIn>
          <div className="text-center">
            <p className="text-koe-stone-muted text-lg">
              Camera and translation interface coming next.
            </p>
          </div>
        </SignedIn>
      </main>

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

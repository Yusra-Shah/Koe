import { useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import useMediaPipe from '../hooks/useMediaPipe'

export default function CameraView({ onLandmarks }) {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const [cameraActive, setCameraActive] = useState(false)
  const [permissionDenied, setPermissionDenied] = useState(false)

  const { landmarks, loading, error } = useMediaPipe(videoRef, canvasRef, cameraActive)

  if (landmarks && onLandmarks) {
    onLandmarks(landmarks)
  }

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
      setCameraActive(true)
      setPermissionDenied(false)
    } catch {
      setPermissionDenied(true)
    }
  }

  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      videoRef.current.srcObject.getTracks().forEach((t) => t.stop())
      videoRef.current.srcObject = null
    }
    setCameraActive(false)
  }

  return (
    <div className="relative bg-koe-stone rounded-koe-lg overflow-hidden aspect-video w-full max-w-2xl">
      <video
        ref={videoRef}
        className="w-full h-full object-cover"
        autoPlay
        playsInline
        muted
        style={{ display: cameraActive ? 'block' : 'none', transform: 'scaleX(-1)' }}
      />
      <canvas
        ref={canvasRef}
        width={640}
        height={480}
        className="absolute inset-0 w-full h-full pointer-events-none"
        style={{ transform: 'scaleX(-1)' }}
      />

      <AnimatePresence>
        {!cameraActive && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="absolute inset-0 flex flex-col items-center justify-center gap-4 bg-koe-stone"
          >
            {permissionDenied ? (
              <div className="text-center px-6">
                <p className="text-koe-amber-light text-lg mb-2">Camera access needed</p>
                <p className="text-koe-stone-muted text-sm">
                  Please allow camera permission in your browser settings to use Koe.
                </p>
              </div>
            ) : (
              <>
                <div className="w-16 h-16 rounded-full border-2 border-koe-amber flex items-center justify-center">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#B45309" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
                    <circle cx="12" cy="13" r="4" />
                  </svg>
                </div>
                <button
                  onClick={startCamera}
                  className="px-6 py-2.5 bg-koe-amber text-white rounded-koe-md text-sm font-medium transition-all duration-200 hover:opacity-90 active:scale-95"
                >
                  Start Camera
                </button>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {cameraActive && (
        <>
          {loading && (
            <div className="absolute top-3 left-3">
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-koe-amber/80 text-white text-xs">
                <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                Loading model...
              </span>
            </div>
          )}

          {!loading && !error && (
            <div className="absolute top-3 left-3">
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-koe-sage/80 text-koe-stone text-xs">
                <span className="w-1.5 h-1.5 rounded-full bg-green-600 animate-pulse" />
                {landmarks ? 'Hand detected' : 'Detecting...'}
              </span>
            </div>
          )}

          {error && (
            <div className="absolute top-3 left-3">
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-koe-sakura/80 text-koe-stone text-xs">
                Error: {error}
              </span>
            </div>
          )}

          <button
            onClick={stopCamera}
            className="absolute top-3 right-3 w-8 h-8 rounded-full bg-koe-stone/60 text-white flex items-center justify-center hover:bg-koe-stone/80 transition-colors duration-200"
            aria-label="Stop camera"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </>
      )}
    </div>
  )
}

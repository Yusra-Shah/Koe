import { useEffect, useRef, useState, useCallback } from 'react'

const HANDS_CDN = 'https://cdn.jsdelivr.net/npm/@mediapipe/hands'
const CAMERA_CDN = 'https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils'

function loadScript(src) {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve()
      return
    }
    const script = document.createElement('script')
    script.src = src
    script.onload = resolve
    script.onerror = reject
    document.head.appendChild(script)
  })
}

const CONNECTIONS = [
  [0,1],[1,2],[2,3],[3,4],
  [0,5],[5,6],[6,7],[7,8],
  [0,9],[9,10],[10,11],[11,12],
  [0,13],[13,14],[14,15],[15,16],
  [0,17],[17,18],[18,19],[19,20],
  [5,9],[9,13],[13,17],
]

export default function useMediaPipe(videoRef, canvasRef, enabled = true) {
  const [landmarks, setLandmarks] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const handsRef = useRef(null)
  const cameraRef = useRef(null)

  const drawLandmarks = useCallback((canvasEl, results) => {
    const ctx = canvasEl.getContext('2d')
    ctx.clearRect(0, 0, canvasEl.width, canvasEl.height)

    if (!results.multiHandLandmarks) return

    for (const hand of results.multiHandLandmarks) {
      ctx.strokeStyle = '#B45309'
      ctx.lineWidth = 2
      for (const [a, b] of CONNECTIONS) {
        ctx.beginPath()
        ctx.moveTo(hand[a].x * canvasEl.width, hand[a].y * canvasEl.height)
        ctx.lineTo(hand[b].x * canvasEl.width, hand[b].y * canvasEl.height)
        ctx.stroke()
      }

      for (const point of hand) {
        const x = point.x * canvasEl.width
        const y = point.y * canvasEl.height
        ctx.beginPath()
        ctx.arc(x, y, 4, 0, 2 * Math.PI)
        ctx.fillStyle = '#FEFCE8'
        ctx.fill()
        ctx.strokeStyle = '#B45309'
        ctx.lineWidth = 1.5
        ctx.stroke()
      }
    }
  }, [])

  useEffect(() => {
    if (!enabled || !videoRef.current) return

    let cancelled = false

    async function init() {
      try {
        await loadScript(`${HANDS_CDN}/hands.js`)
        await loadScript(`${CAMERA_CDN}/camera_utils.js`)

        if (cancelled) return

        const hands = new window.Hands({
          locateFile: (file) => `${HANDS_CDN}/${file}`,
        })

        hands.setOptions({
          maxNumHands: 2,
          modelComplexity: 1,
          minDetectionConfidence: 0.7,
          minTrackingConfidence: 0.5,
        })

        hands.onResults((results) => {
          if (results.multiHandLandmarks?.length > 0) {
            setLandmarks(results.multiHandLandmarks)
          } else {
            setLandmarks(null)
          }
          if (canvasRef.current) {
            drawLandmarks(canvasRef.current, results)
          }
        })

        handsRef.current = hands

        const camera = new window.Camera(videoRef.current, {
          onFrame: async () => {
            await hands.send({ image: videoRef.current })
          },
          width: 640,
          height: 480,
        })

        await camera.start()
        cameraRef.current = camera
        setLoading(false)
      } catch (err) {
        if (!cancelled) {
          setError(err.message || 'Failed to initialize MediaPipe')
          setLoading(false)
        }
      }
    }

    init()

    return () => {
      cancelled = true
      cameraRef.current?.stop()
      handsRef.current?.close()
    }
  }, [enabled, videoRef, canvasRef, drawLandmarks])

  return { landmarks, loading, error }
}

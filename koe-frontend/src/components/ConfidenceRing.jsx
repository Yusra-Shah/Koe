import { motion } from 'framer-motion'

export default function ConfidenceRing({ confidence = 0, size = 80 }) {
  const strokeWidth = 4
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const filled = circumference * confidence
  const percent = Math.round(confidence * 100)

  const getColor = () => {
    if (confidence >= 0.75) return '#B45309'
    if (confidence >= 0.5) return '#D97706'
    return '#78716C'
  }

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#E7E5E4"
          strokeWidth={strokeWidth}
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={getColor()}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: circumference - filled }}
          transition={{ duration: 0.6, ease: [0.25, 0.1, 0.25, 1] }}
        />
      </svg>
      <span
        className="absolute text-sm font-medium"
        style={{ color: getColor() }}
        aria-label={`Confidence ${percent} percent`}
      >
        {percent}%
      </span>
    </div>
  )
}

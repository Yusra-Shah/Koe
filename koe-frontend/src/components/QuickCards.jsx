import { motion } from 'framer-motion'
import useTTS from '../hooks/useTTS'

const QUICK_PHRASES = [
  { id: 1, en: 'I need help',       ur: 'مجھے مدد چاہیے',     icon: '🆘' },
  { id: 2, en: 'I am in pain',      ur: 'مجھے درد ہے',        icon: '😣' },
  { id: 3, en: 'Call a doctor',     ur: 'ڈاکٹر کو بلائیں',   icon: '👨‍⚕️' },
  { id: 4, en: 'I need water',      ur: 'مجھے پانی چاہیے',   icon: '💧' },
  { id: 5, en: 'I have an allergy', ur: 'مجھے الرجی ہے',      icon: '⚠️' },
  { id: 6, en: 'Call my family',    ur: 'میرے گھر والوں کو بلائیں', icon: '👨‍👩‍👧' },
  { id: 7, en: 'Call an ambulance', ur: 'ایمبولینس بلائیں',   icon: '🚑' },
  { id: 8, en: 'Yes',               ur: 'ہاں',                icon: '✅' },
  { id: 9, en: 'No',                ur: 'نہیں',               icon: '❌' },
  { id: 10, en: 'Thank you',        ur: 'شکریہ',              icon: '🙏' },
]

function QuickCard({ phrase, language, onSpeak }) {
  const displayText = language === 'ur' ? phrase.ur : phrase.en

  return (
    <motion.button
      whileTap={{ scale: 0.95 }}
      onClick={() => onSpeak(displayText, language)}
      className="flex flex-col items-center gap-1.5 p-3 rounded-koe-lg bg-koe-amber-light hover:bg-koe-amber-pale border border-koe-border transition-colors duration-200 text-center min-h-[80px] justify-center"
      aria-label={`Speak: ${phrase.en}`}
    >
      <span className="text-xl" role="img" aria-hidden="true">{phrase.icon}</span>
      <span className="text-koe-stone text-xs font-medium leading-tight line-clamp-2">
        {displayText}
      </span>
    </motion.button>
  )
}

export default function QuickCards({ language }) {
  const { speak } = useTTS()

  return (
    <div className="bg-white border border-koe-border rounded-koe-lg p-4">
      <h3 className="text-koe-stone-muted text-xs font-medium uppercase tracking-wide mb-3">
        Quick Signs
      </h3>
      <div className="grid grid-cols-5 gap-2">
        {QUICK_PHRASES.map((phrase) => (
          <QuickCard
            key={phrase.id}
            phrase={phrase}
            language={language}
            onSpeak={speak}
          />
        ))}
      </div>
    </div>
  )
}

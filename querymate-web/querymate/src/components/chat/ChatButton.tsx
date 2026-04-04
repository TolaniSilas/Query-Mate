'use client'
import { MessageSquare, X } from 'lucide-react'


interface ChatButtonProps {
  isOpen:  boolean
  onClick: () => void
}

export default function ChatButton({ isOpen, onClick }: ChatButtonProps) {
  return (
    <div style={{ position: 'fixed', bottom: 28, right: 28, zIndex: 100 }}>
      {/* tooltip */}
      {!isOpen && (
        <div
          style={{
            position: 'absolute', right: '100%', top: '50%', transform: 'translateY(-50%)',
            marginRight: 12, backgroundColor: '#0D0D0D', color: '#F4F1EB',
            fontFamily: 'var(--font-sans)', fontSize: 12, padding: '7px 12px',
            borderRadius: 3, whiteSpace: 'nowrap', pointerEvents: 'none',
            opacity: 0, transition: 'opacity 0.2s',
          }}
          className="chat-tooltip"
        >
          Ask your database
        </div>
      )}

      <button
        onClick={onClick}
        aria-label={isOpen ? 'Close chat': 'Open QueryMate chat'}
        style={{
          width: 52, height: 52, borderRadius: '50%',
          backgroundColor: isOpen ? '#2a2a2a': '#B8924A',
          border: 'none', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 4px 20px rgba(0,0,0,0.18)',
          transition: 'background 0.2s, transform 0.2s',
        }}
        onMouseEnter={e => {
          e.currentTarget.style.transform = 'scale(1.08)'
          const tip = e.currentTarget.parentElement?.querySelector('.chat-tooltip') as HTMLElement
          if (tip) tip.style.opacity = '1'
        }}
        onMouseLeave={e => {
          e.currentTarget.style.transform = 'scale(1)'
          const tip = e.currentTarget.parentElement?.querySelector('.chat-tooltip') as HTMLElement
          if (tip) tip.style.opacity = '0'
        }}
      >
        {isOpen
          ? <X size={20} color="#F4F1EB" strokeWidth={2}/>
          : <MessageSquare size={20} color="#0D0D0D"  strokeWidth={1.8}/>
        }
      </button>
    </div>
  )
}
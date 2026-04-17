'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Database, Menu, X } from 'lucide-react'

const NAV = [
  { label: 'About', href: '#about' },
  { label: 'Services', href: '#services' },
  { label: 'Package', href: '#package' },
  { label: 'Architecture', href: '#architecture' },
  { label: 'Security', href: '#security' },
]

export default function Header({ onTryChat }: { onTryChat?: () => void }) {
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const router = useRouter()

  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 32)
    window.addEventListener('scroll', fn, { passive: true })
    return () => window.removeEventListener('scroll', fn)
  }, [])

  const go = (href: string) => {
    if (href === '#') return
    setMenuOpen(false)
    document.querySelector(href)?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <header
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 50,
        backgroundColor: scrolled ? 'rgba(244,241,235,0.97)' : 'transparent',
        borderBottom: scrolled ? '1px solid #E8E3D8' : '1px solid transparent',
        backdropFilter: scrolled ? 'blur(12px)' : 'none',
        transition: 'all 0.3s ease',
      }}
    >
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 32px', height: 64, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>

        {/* logo */}
        <a
          href="#"
          onClick={e => { e.preventDefault(); window.scrollTo({ top: 0, behavior: 'smooth' }) }}
          style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none' }}
        >
          <div style={{ width: 32, height: 32, backgroundColor: '#0D0D0D', borderRadius: 3, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Database size={15} color="#F4F1EB" strokeWidth={1.5} />
          </div>
          <span style={{ fontFamily: 'var(--font-display)', fontSize: 18, fontWeight: 500, color: '#0D0D0D', letterSpacing: '-0.02em' }}>
            Query<span style={{ color: '#B8924A' }}>Mate</span>
          </span>
        </a>

        {/* desktop nav */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: 32 }} className="hidden-mobile">
          {NAV.map(n => (
            <button
              key={n.label}
              onClick={() => go(n.href)}
              className="font-space"
              style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 14, fontWeight: 500, color: '#7A7670', letterSpacing: '0.01em', transition: 'color 0.2s' }}
              onMouseEnter={e => (e.currentTarget.style.color = '#0D0D0D')}
              onMouseLeave={e => (e.currentTarget.style.color = '#7A7670')}
            >
              {n.label}
            </button>
          ))}
        </nav>

        {/* desktop cta */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 20 }} className="hidden-mobile">
          <a
            href="https://github.com/TolaniSilas/Query-Mate/"
            target="_blank"
            rel="noopener noreferrer"
            className="font-space"
            style={{ fontSize: 14, fontWeight: 500, color: '#7A7670', textDecoration: 'none', transition: 'color 0.2s' }}
            onMouseEnter={e => (e.currentTarget.style.color = '#0D0D0D')}
            onMouseLeave={e => (e.currentTarget.style.color = '#7A7670')}
          >
            GitHub
          </a>
          <button
            className="font-space"
            style={{
              fontSize: 13,
              fontWeight: 500,
              backgroundColor: 'transparent',
              border: '1px solid #B8924A',
              color: '#B8924A',
              padding: '6px 14px',
              borderRadius: 3,
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseEnter={e => { e.currentTarget.style.backgroundColor = 'rgba(184, 146, 74, 0.05)' }}
            onMouseLeave={e => { e.currentTarget.style.backgroundColor = 'transparent' }}
            onClick={onTryChat}
          >
            Try Chat
          </button>
          {/* <button
            className="font-space"
            style={{
              fontSize: 13,
              fontWeight: 600,
              backgroundColor: '#0D0D0D',
              color: '#F4F1EB',
              padding: '6px 18px',
              borderRadius: 3,
              border: 'none',
              cursor: 'pointer',
              transition: 'background 0.2s',
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
            }}
            onMouseEnter={e => (e.currentTarget.style.backgroundColor = '#2a2a2a')}
            onMouseLeave={e => (e.currentTarget.style.backgroundColor = '#0D0D0D')}
          >
            Sign in
          </button> */}
        </div>

        {/* mobile hamburger */}
        <button
          onClick={() => setMenuOpen(!menuOpen)}
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#0D0D0D', display: 'none' }}
          className="show-mobile"
          aria-label="Toggle menu"
        >
          {menuOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* mobile menu */}
      {
        menuOpen && (
          <div style={{ backgroundColor: '#F4F1EB', borderTop: '1px solid #E8E3D8', padding: '16px 32px 24px' }}>
            {NAV.map(n => (
              <button
                key={n.label}
                onClick={() => go(n.href)}
                style={{ display: 'block', width: '100%', textAlign: 'left', background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'var(--font-space)', fontSize: 15, fontWeight: 500, color: '#7A7670', padding: '10px 0', borderBottom: '1px solid #E8E3D8' }}
              >
                {n.label}
              </button>
            ))}
            <button
              style={{ display: 'block', width: '100%', marginTop: 12, fontFamily: 'var(--font-space)', fontSize: 13, fontWeight: 500, backgroundColor: 'transparent', border: '1px solid #B8924A', color: '#B8924A', padding: '12px 16px', borderRadius: 3, textAlign: 'center', cursor: 'pointer' }}
              onClick={onTryChat}
            >
              Try Chat
            </button>
            <button
              style={{ display: 'block', width: '100%', marginTop: 12, fontFamily: 'var(--font-space)', fontSize: 14, fontWeight: 600, backgroundColor: '#0D0D0D', color: '#F4F1EB', padding: '12px 16px', borderRadius: 3, border: 'none', textAlign: 'center' }}
              onClick={() => { setMenuOpen(false); router.push('/signin') }}
            >
              Sign in
            </button>
          </div>
        )
      }

      <style>{`
        @media (max-width: 768px) {
          .hidden-mobile { display: none !important; }
          .show-mobile   { display: block !important; }
        }
      `}</style>
    </header >
  )
}
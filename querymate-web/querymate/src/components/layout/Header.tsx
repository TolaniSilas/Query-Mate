'use client'
import {useState, useEffect} from 'react'
import {Database, Menu, X} from 'lucide-react'

const NAV = [
  {label: 'About', href: '#about'},
  {label: 'Services', href: '#services'},
  {label: 'Architecture', href: '#architecture'},
  {label: 'Security', href: '#security'},
]

export default function Header() {
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 32)
    window.addEventListener('scroll', fn, { passive: true })
    return () => window.removeEventListener('scroll', fn)
  }, [])

  const go = (href: string) => {
    setMenuOpen(false)
    document.querySelector(href)?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <header
      style={{
        position:         'fixed',
        top: 0,
        left:             0,
        right:            0,
        zIndex:           50,
        backgroundColor:  scrolled ? 'rgba(244,241,235,0.97)' : 'transparent',
        borderBottom:     scrolled ? '1px solid #E8E3D8' : '1px solid transparent',
        backdropFilter:   scrolled ? 'blur(12px)' : 'none',
        transition:       'all 0.3s ease',
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
        <nav style={{ display: 'flex', alignItems: 'center', gap: 36 }} className="hidden-mobile">
          {NAV.map(n => (
            <button
              key={n.href}
              onClick={() => go(n.href)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'var(--font-sans)', fontSize: 14, color: '#7A7670', letterSpacing: '0.01em', transition: 'color 0.2s' }}
              onMouseEnter={e => (e.currentTarget.style.color = '#0D0D0D')}
              onMouseLeave={e => (e.currentTarget.style.color = '#7A7670')}
            >
              {n.label}
            </button>
          ))}
        </nav>

        {/* desktop cta */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }} className="hidden-mobile">
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            style={{ fontFamily: 'var(--font-sans)', fontSize: 13, color: '#7A7670', textDecoration: 'none', transition: 'color 0.2s' }}
            onMouseEnter={e => (e.currentTarget.style.color = '#0D0D0D')}
            onMouseLeave={e => (e.currentTarget.style.color = '#7A7670')}
          >
            GitHub
          </a>
          <a
            href="https://pypi.org"
            target="_blank"
            rel="noopener noreferrer"
            style={{ fontFamily: 'var(--font-mono)', fontSize: 12, backgroundColor: '#0D0D0D', color: '#F4F1EB', padding: '8px 16px', borderRadius: 3, textDecoration: 'none', transition: 'background 0.2s' }}
            onMouseEnter={e => (e.currentTarget.style.backgroundColor = '#2a2a2a')}
            onMouseLeave={e => (e.currentTarget.style.backgroundColor = '#0D0D0D')}
          >
            pip install
          </a>
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
      {menuOpen && (
        <div style={{ backgroundColor: '#F4F1EB', borderTop: '1px solid #E8E3D8', padding: '16px 32px 24px' }}>
          {NAV.map(n => (
            <button
              key={n.href}
              onClick={() => go(n.href)}
              style={{ display: 'block', width: '100%', textAlign: 'left', background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'var(--font-sans)', fontSize: 15, color: '#7A7670', padding: '10px 0', borderBottom: '1px solid #E8E3D8' }}
            >
              {n.label}
            </button>
          ))}
          <a
            href="https://pypi.org"
            target="_blank"
            rel="noopener noreferrer"
            style={{ display: 'block', marginTop: 16, fontFamily: 'var(--font-mono)', fontSize: 13, backgroundColor: '#0D0D0D', color: '#F4F1EB', padding: '10px 16px', borderRadius: 3, textDecoration: 'none', textAlign: 'center' }}
          >
            pip install querymate
          </a>
        </div>
      )}

      <style>{`
        @media (max-width: 768px) {
          .hidden-mobile { display: none !important; }
          .show-mobile   { display: block !important; }
        }
      `}</style>
    </header>
  )
}
'use client'

import { ArrowDown, Terminal, Shield, Zap, Database } from 'lucide-react'

const PILLS = [
  { Icon: Terminal, label: 'Multi-Agent Pipeline' },
  { Icon: Shield,   label: 'Read-Only Enforced'   },
  { Icon: Database, label: 'PostgreSQL · MySQL · SQLite' },
  { Icon: Zap,      label: '4 LLM Providers'       },
]

export default function Hero() {
  return (
    <section
      style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', paddingTop: 64, position: 'relative', overflow: 'hidden' }}
    >
      {/* fine dot grid background */}
      <div
        aria-hidden
        style={{
          position:    'absolute', inset: 0, pointerEvents: 'none',
          backgroundImage: 'radial-gradient(circle, #0D0D0D18 1px, transparent 1px)',
          backgroundSize:  '28px 28px',
        }}
      />

      {/* large watermark text */}
      <div
        aria-hidden
        style={{
          position:  'absolute', top: '50%', left: '50%',
          transform: 'translate(-50%, -50%)',
          fontFamily: 'var(--font-display)', fontSize: 'clamp(80px, 18vw, 240px)',
          fontWeight: 400, color: 'rgba(13,13,13,0.028)',
          whiteSpace: 'nowrap', pointerEvents: 'none', userSelect: 'none',
          lineHeight: 1,
        }}
      >
        QueryMate
      </div>

      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 32px', position: 'relative', zIndex: 1, width: '100%' }}>

        {/* eyebrow */}
        <div className="reveal-up" style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 32 }}>
          <div style={{ height: 1, width: 32, backgroundColor: '#B8924A' }} />
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: '#B8924A', textTransform: 'uppercase', letterSpacing: '0.15em' }}>
            Text-to-SQL · Multi-Agent · Secure
          </span>
        </div>

        {/* headline */}
        <h1
          className="reveal-up delay-100"
          style={{
            fontFamily: 'var(--font-display)',
            fontSize:   'clamp(52px, 9vw, 108px)',
            fontWeight: 400,
            lineHeight: 0.95,
            color:      '#0D0D0D',
            letterSpacing: '-0.02em',
            marginBottom: 32,
          }}
        >
          Ask your database
          <br />
          <em style={{ fontStyle: 'italic', color: '#B8924A' }}>anything.</em>
        </h1>

        {/* subheading */}
        <p
          className="reveal-up delay-200"
          style={{
            fontFamily: 'var(--font-sans)', fontSize: 18, color: '#7A7670',
            maxWidth: 520, lineHeight: 1.7, marginBottom: 40,
          }}
        >
          QueryMate translates plain English questions into precise SQL queries
          and returns human-readable answers — powered by a multi-agent pipeline
          with layered read-only security enforcement.
        </p>

        {/* code block */}
        <div className="reveal-up delay-300" style={{ display: 'inline-block', marginBottom: 40 }}>
          <div style={{ backgroundColor: '#0D0D0D', borderRadius: 4, overflow: 'hidden', border: '1px solid #2a2a2a' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '8px 14px', borderBottom: '1px solid #1e1e1e' }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: '#2a2a2a' }} />
              <div style={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: '#2a2a2a' }} />
              <div style={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: '#2a2a2a' }} />
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'rgba(244,241,235,0.25)', marginLeft: 6 }}>python</span>
            </div>
            <pre style={{ padding: '16px 20px', fontFamily: 'var(--font-mono)', fontSize: 13, lineHeight: 1.8, overflowX: 'auto' }}>
              <span style={{ color: 'rgba(244,241,235,0.4)' }}>from </span>
              <span style={{ color: '#B8924A' }}>querymate </span>
              <span style={{ color: 'rgba(244,241,235,0.4)' }}>import </span>
              <span style={{ color: '#F4F1EB' }}>QueryMate{'\n'}</span>
              <span style={{ color: 'rgba(244,241,235,0.4)' }}>{'\n'}</span>
              <span style={{ color: '#F4F1EB' }}>qm </span>
              <span style={{ color: 'rgba(244,241,235,0.4)' }}>= </span>
              <span style={{ color: '#F4F1EB' }}>QueryMate(db_type</span>
              <span style={{ color: 'rgba(244,241,235,0.4)' }}>=</span>
              <span style={{ color: '#B8924A' }}>&quot;postgresql&quot;</span>
              <span style={{ color: '#F4F1EB' }}>, database_url</span>
              <span style={{ color: 'rgba(244,241,235,0.4)' }}>=</span>
              <span style={{ color: '#B8924A' }}>url</span>
              <span style={{ color: '#F4F1EB' }}>){'\n'}</span>
              <span style={{ color: '#F4F1EB' }}>result </span>
              <span style={{ color: 'rgba(244,241,235,0.4)' }}>= </span>
              <span style={{ color: '#F4F1EB' }}>qm.ask(</span>
              <span style={{ color: '#B8924A' }}>&quot;Which merchant had the highest revenue?&quot;</span>
              <span style={{ color: '#F4F1EB' }}>){'\n'}</span>
              <span style={{ color: 'rgba(244,241,235,0.5)' }}>print</span>
              <span style={{ color: '#F4F1EB' }}>(result.answer)</span>
            </pre>
          </div>
        </div>

        {/* pills */}
        <div className="reveal-up delay-400" style={{ display: 'flex', flexWrap: 'wrap', gap: 10, marginBottom: 48 }}>
          {PILLS.map(({ Icon, label }) => (
            <div
              key={label}
              style={{
                display: 'flex', alignItems: 'center', gap: 8,
                padding: '7px 14px', border: '1px solid #E8E3D8',
                borderRadius: 100, backgroundColor: 'rgba(244,241,235,0.7)',
              }}
            >
              <Icon size={12} color="#B8924A" strokeWidth={1.5} />
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: '#7A7670' }}>{label}</span>
            </div>
          ))}
        </div>

        {/* cta buttons */}
        <div className="reveal-up delay-500" style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
          <a
            href="https://pypi.org"
            target="_blank"
            rel="noopener noreferrer"
            style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '12px 24px', backgroundColor: '#0D0D0D', color: '#F4F1EB', fontFamily: 'var(--font-sans)', fontSize: 14, fontWeight: 500, borderRadius: 3, textDecoration: 'none', transition: 'background 0.2s' }}
            onMouseEnter={e => (e.currentTarget.style.backgroundColor = '#2a2a2a')}
            onMouseLeave={e => (e.currentTarget.style.backgroundColor = '#0D0D0D')}
          >
            Get Started
            <ArrowDown size={14} style={{ transform: 'rotate(-90deg)' }} />
          </a>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '12px 24px', border: '1px solid #E8E3D8', color: '#0D0D0D', fontFamily: 'var(--font-sans)', fontSize: 14, fontWeight: 500, borderRadius: 3, textDecoration: 'none', transition: 'background 0.2s' }}
            onMouseEnter={e => (e.currentTarget.style.backgroundColor = '#E8E3D8')}
            onMouseLeave={e => (e.currentTarget.style.backgroundColor = 'transparent')}
          >
            View on GitHub
          </a>
        </div>
      </div>

      {/* scroll cue */}
      <button
        onClick={() => document.querySelector('#about')?.scrollIntoView({ behavior: 'smooth' })}
        style={{ position: 'absolute', bottom: 32, left: '50%', transform: 'translateX(-50%)', background: 'none', border: 'none', cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, color: '#7A7670', transition: 'color 0.2s' }}
        aria-label="Scroll down"
        onMouseEnter={e => (e.currentTarget.style.color = '#0D0D0D')}
        onMouseLeave={e => (e.currentTarget.style.color = '#7A7670')}
      >
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.12em' }}>Scroll</span>
        <ArrowDown size={14} />
      </button>
    </section>
  )
}
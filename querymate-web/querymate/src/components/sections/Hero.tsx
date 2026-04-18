'use client'

import Image from 'next/image'
import Link from 'next/link'
import { ArrowDown, Terminal, Shield, Database } from 'lucide-react'

export default function Hero() {
  return (
    <section
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        paddingTop: 80,
        position: 'sticky',
        top: 0,
        zIndex: 0,
        overflow: 'hidden'
      }}
    >
      {/* fine dot grid background */}
      <div
        aria-hidden
        style={{
          position: 'absolute', inset: 0, pointerEvents: 'none',
          backgroundImage: 'radial-gradient(circle, #0D0D0D18 1px, transparent 1px)',
          backgroundSize: '28px 28px',
        }}
      />

      {/* large watermark text */}
      <div
        aria-hidden
        style={{
          position: 'absolute', top: '50%', left: '50%',
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
        <div className="hero-grid">
          {/* left column: headline and info */}
          <div className="reveal-up">
            {/* eyebrow */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 32 }}>
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
                fontSize: 'clamp(48px, 6vw, 84px)',
                fontWeight: 400,
                lineHeight: 0.95,
                color: '#0D0D0D',
                letterSpacing: '-0.02em',
                marginBottom: 24,
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
                fontFamily: 'var(--font-sans)', fontSize: 17, color: '#7A7670',
                maxWidth: 480, lineHeight: 1.6, marginBottom: 32,
              }}
            >
              QueryMate translates plain English questions into precise SQL queries
              and returns human-readable answers — powered by a multi-agent pipeline
              with layered read-only security enforcement.
            </p>

            <div className="reveal-up delay-600" style={{ display: 'flex', flexWrap: 'wrap', gap: 16, marginBottom: 40 }}>
              <Link
                href="/signup"
                className="font-space"
                style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 600, backgroundColor: '#0D0D0D', color: '#F4F1EB', padding: '12px 32px', borderRadius: 4, border: 'none', cursor: 'pointer', boxShadow: '0 10px 30px rgba(0,0,0,0.1)', textDecoration: 'none' }}
              >
                Sign Up Now
              </Link>
              <button
                className="font-space"
                style={{ fontSize: 14, fontWeight: 600, backgroundColor: 'transparent', color: '#0D0D0D', padding: '12px 32px', borderRadius: 4, border: '1px solid #E8E3D8', cursor: 'pointer' }}
              >
                Learn More
              </button>
            </div>

            {/* pills */}
            <div className="reveal-up delay-400" style={{ display: 'flex', flexWrap: 'wrap', gap: 10, marginBottom: 40 }}>
              {[
                { Icon: Terminal, label: 'Multi-Agent' },
                { Icon: Shield, label: 'Read-Only' },
                { Icon: Database, label: 'SQL' },
              ].map(({ Icon, label }) => (
                <div
                  key={label}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 8,
                    padding: '6px 12px', border: '1px solid #E8E3D8',
                    borderRadius: 100, backgroundColor: 'rgba(244,241,235,0.7)',
                  }}
                >
                  <Icon size={12} color="#B8924A" strokeWidth={1.5} />
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: '#7A7670' }}>{label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* right column: product preview */}
          <div className="reveal-up" style={{ display: 'flex', justifyContent: 'flex-start', perspective: '1000px', position: 'relative', minHeight: '600px' }}>
            <div
              className="reveal-up delay-600"
              style={{
                position: 'absolute',
                top: '0px',
                left: '40px',
                transform: 'perspective(1500px) rotateY(-12deg) rotateX(4deg) scale(1.3)',
                width: 'max(600px, 50vw)',
                borderRadius: '16px',
                overflow: 'hidden',
                transition: 'all 0.8s cubic-bezier(0.23, 1, 0.32, 1)',
                boxShadow: '0 80px 150px rgba(0,0,0,0.3), 0 0 100px rgba(184, 146, 74, 0.1)',
                border: '1px solid rgba(184, 146, 74, 0.3)',
                zIndex: 2,
                transformOrigin: 'left top',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'perspective(1500px) rotateY(-4deg) rotateX(2deg) scale(1.35)';
                e.currentTarget.style.boxShadow = '0 100px 200px rgba(0,0,0,0.4), 0 0 180px rgba(184, 146, 74, 0.15)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'perspective(1500px) rotateY(-12deg) rotateX(4deg) scale(1.3)';
                e.currentTarget.style.boxShadow = '0 80px 150px rgba(0,0,0,0.3), 0 0 100px rgba(184, 146, 74, 0.1)';
              }}
            >
              <Image
                src="/images/hero_chat_preview_image.png"
                alt="QueryMate Dashboard Preview"
                width={1600}
                height={1280}
                sizes="(max-width: 768px) 100vw, 50vw"
                style={{ width: '100%', height: 'auto', display: 'block' }}
              />
            </div>
          </div>
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

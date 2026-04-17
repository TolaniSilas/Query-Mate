'use client'

import React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Eye, Mail, Lock } from 'lucide-react'

export default function AuthSection({ mode = 'signin' }: { mode?: 'signin' | 'signup' }) {
  const isSignUp = mode === 'signup'
  const router = useRouter()

  return (
    <div
      className="reveal-up delay-600"
      style={{
        backgroundColor: 'var(--panel)',
        padding: '32px',
        borderRadius: '8px',
        border: '1px solid rgba(184, 146, 74, 0.2)',
        color: '#F4F1EB',
        width: '100%',
        maxWidth: '420px',
        boxShadow: '0 20px 40px rgba(0,0,0,0.4)',
        position: 'relative',
        zIndex: 10
      }}
    >
      <h2
        className="font-space"
        style={{
          fontSize: '20px',
          fontWeight: 500,
          marginBottom: '24px',
          color: '#F4F1EB'
        }}>
        {isSignUp ? 'Create your account' : 'Sign in to your account'}
      </h2>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {/* email field */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <label className="font-space" style={{ fontSize: '12px', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Email
          </label>
          <div style={{ position: 'relative' }}>
            <input
              type="email"
              placeholder="name@company.com"
              style={{
                width: '100%',
                padding: '12px 16px',
                backgroundColor: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '4px',
                color: '#F4F1EB',
                fontFamily: 'var(--font-sans)',
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 0.2s'
              }}
              onFocus={(e) => e.currentTarget.style.borderColor = 'var(--gold)'}
              onBlur={(e) => e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'}
            />
            <Mail size={16} color="var(--muted)" style={{ position: 'absolute', right: '16px', top: '50%', transform: 'translateY(-50%)', opacity: 0.5 }} />
          </div>
        </div>

        {/* password field */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <label className="font-space" style={{ fontSize: '12px', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Password
            </label>
            <button className="font-space" style={{ background: 'none', border: 'none', color: 'var(--gold)', fontSize: '12px', cursor: 'pointer' }}>
              Forgot password?
            </button>
          </div>
          <div style={{ position: 'relative' }}>
            <input
              type="password"
              placeholder="••••••••"
              style={{
                width: '100%',
                padding: '12px 16px',
                backgroundColor: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '4px',
                color: '#F4F1EB',
                fontFamily: 'var(--font-sans)',
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 0.2s'
              }}
              onFocus={(e) => e.currentTarget.style.borderColor = 'var(--gold)'}
              onBlur={(e) => e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'}
            />
            <Eye size={16} color="var(--muted)" style={{ position: 'absolute', right: '16px', top: '50%', transform: 'translateY(-50%)', opacity: 0.5, cursor: 'pointer' }} />
          </div>
        </div>

        <button
          className="font-space"
          onClick={() => router.push('/connect')}
          style={{
            marginTop: '8px',
            backgroundColor: 'var(--gold)',
            color: 'var(--ink)',
            padding: '12px',
            borderRadius: '4px',
            border: 'none',
            fontSize: '14px',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            transition: 'transform 0.1s, opacity 0.2s'
          }}
          onMouseDown={(e) => e.currentTarget.style.transform = 'scale(0.98)'}
          onMouseUp={(e) => e.currentTarget.style.transform = 'scale(1)'}
          onMouseEnter={(e) => e.currentTarget.style.opacity = '0.9'}
          onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
        >
          {isSignUp ? 'Create account' : 'Continue'}
          <Lock size={14} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', margin: '8px 0' }}>
          <div style={{ flex: 1, height: '1px', backgroundColor: 'rgba(255,255,255,0.1)' }} />
          <span style={{ fontSize: '12px', color: 'var(--muted)', fontFamily: 'var(--font-space)' }}>OR</span>
          <div style={{ flex: 1, height: '1px', backgroundColor: 'rgba(255,255,255,0.1)' }} />
        </div>

        <button
          className="font-space"
          style={{
            backgroundColor: 'transparent',
            color: '#F4F1EB',
            padding: '12px',
            borderRadius: '4px',
            border: '1px solid rgba(255,255,255,0.1)',
            fontSize: '14px',
            fontWeight: 500,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '12px',
            transition: 'background-color 0.2s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.05)'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
        >
          <svg width="18" height="18" viewBox="0 0 18 18">
            <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z" fill="#4285F4" />
            <path d="M9 18c2.43 0 4.467-.806 5.956-2.184L12.048 13.56c-.819.549-1.868.873-3.048.873-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z" fill="#34A853" />
            <path d="M3.964 10.722a5.41 5.41 0 010-3.444V4.946H.957a8.997 8.997 0 000 8.108l3.007-2.332z" fill="#FBBC05" />
            <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.946l3.007 2.332C4.672 5.164 6.656 3.58 9 3.58z" fill="#EA4335" />
          </svg>
          Continue with Google
        </button>
      </div>

      <p style={{ marginTop: '24px', textAlign: 'center', fontSize: '13px', color: 'var(--muted)', fontFamily: 'var(--font-space)' }}>
        {isSignUp ? 'Already have an account? ' : 'No account? '}
        <Link
          href={isSignUp ? '/signin' : '/signup'}
          style={{ color: 'var(--gold)', fontWeight: 600, textDecoration: 'none', cursor: 'pointer' }}
        >
          {isSignUp ? 'Sign in' : 'Sign up'}
        </Link>
      </p>

      <div style={{ position: 'absolute', top: -5, right: -5, display: 'grid', gridTemplateColumns: 'repeat(3, 3px)', gap: '3px', opacity: 0.3 }}>
        {[...Array(9)].map((_, i) => <div key={i} style={{ width: '3px', height: '3px', backgroundColor: 'var(--gold)', borderRadius: '50%' }} />)}
      </div>
    </div>
  )
}

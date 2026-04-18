'use client'

import Link from 'next/link'
import { Database, Terminal, ShieldCheck, Box } from 'lucide-react'
import { useScrollReveal } from '@/src/components/utils/useScrollReveal'

export default function Package() {
    const rootRef = useScrollReveal<HTMLDivElement>()

    return (
        <section id="package" style={{ padding: '112px 0', backgroundColor: '#F9F7F2' }}>
            <div ref={rootRef} style={{ maxWidth: 1200, margin: '0 auto', padding: '0 32px' }}>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '64px', alignItems: 'center' }}>

                    <div>
                        <div data-scroll-reveal className="scroll-reveal delay-100" style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
                            <div style={{ height: 1, width: 32, backgroundColor: '#B8924A' }} />
                            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: '#B8924A', textTransform: 'uppercase', letterSpacing: '0.15em' }}>Developer Package</span>
                        </div>
                        <h2 data-scroll-reveal className="scroll-reveal delay-200" style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(32px, 4vw, 48px)', fontWeight: 400, color: '#0D0D0D', marginBottom: 24, letterSpacing: '-0.02em', lineHeight: 1.1 }}>
                            Secured Python Library <br />
                            <em style={{ fontStyle: 'italic' }}>for Your Backend</em>
                        </h2>
                        <p data-scroll-reveal className="scroll-reveal delay-300" style={{ fontFamily: 'var(--font-sans)', fontSize: 15, color: '#7A7670', lineHeight: 1.7, marginBottom: 32 }}>
                            QueryMate isn&apos;t just a web interface. It&apos;s a fully-featured Python package designed to be integrated into your existing services. Translate natural language into secure, validated SQL with just a few lines of code.
                        </p>

                        <div data-scroll-reveal className="scroll-reveal delay-400" style={{ display: 'flex', flexWrap: 'wrap', gap: 24, marginBottom: 40 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                <Terminal size={16} color="#B8924A" />
                                <span style={{ fontFamily: 'var(--font-sans)', fontSize: 14, color: '#0D0D0D', fontWeight: 500 }}>pip install querymate</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                <ShieldCheck size={16} color="#B8924A" />
                                <span style={{ fontFamily: 'var(--font-sans)', fontSize: 14, color: '#0D0D0D', fontWeight: 500 }}>Secure by Default</span>
                            </div>
                        </div>

                        <div data-scroll-reveal className="scroll-reveal delay-500" style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
                            <a
                                href="https://pypi.org/project/query-mate/"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="font-space"
                                style={{
                                    display: 'inline-flex',
                                    alignItems: 'center',
                                    gap: 10,
                                    fontSize: 14,
                                    fontWeight: 600,
                                    backgroundColor: '#0D0D0D',
                                    color: '#F4F1EB',
                                    padding: '12px 24px',
                                    borderRadius: 4,
                                    textDecoration: 'none',
                                    transition: 'all 0.2s',
                                    boxShadow: '0 10px 30px rgba(0,0,0,0.1)'
                                }}
                                onMouseEnter={e => { e.currentTarget.style.backgroundColor = '#2a2a2a' }}
                                onMouseLeave={e => { e.currentTarget.style.backgroundColor = '#0D0D0D' }}
                            >
                                <Box size={16} />
                                View on PyPI
                            </a>

                            <Link
                                href="/docs"
                                className="font-space"
                                style={{
                                    display: 'inline-flex',
                                    alignItems: 'center',
                                    gap: 10,
                                    fontSize: 14,
                                    fontWeight: 600,
                                    backgroundColor: '#F4F1EB',
                                    color: '#0D0D0D',
                                    padding: '12px 24px',
                                    borderRadius: 4,
                                    textDecoration: 'none',
                                    transition: 'all 0.2s',
                                    border: '1px solid #E8E3D8',
                                    boxShadow: '0 10px 30px rgba(184,146,74,0.08)'
                                }}
                                onMouseEnter={e => {
                                    e.currentTarget.style.backgroundColor = '#EFE7D8'
                                    e.currentTarget.style.borderColor = '#D9CDB8'
                                }}
                                onMouseLeave={e => {
                                    e.currentTarget.style.backgroundColor = '#F4F1EB'
                                    e.currentTarget.style.borderColor = '#E8E3D8'
                                }}
                            >
                                <Database size={16} />
                                Read the Docs
                            </Link>
                        </div>
                    </div>

                    <div data-scroll-reveal className="scroll-reveal delay-600" style={{ display: 'flex', justifyContent: 'center' }}>
                        <div style={{ backgroundColor: '#161616', borderRadius: 8, overflow: 'hidden', border: '1px solid #2a2a2a', boxShadow: '0 30px 60px rgba(0,0,0,0.3)', width: '100%', maxWidth: 500 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '12px 18px', borderBottom: '1px solid #1e1e1e', backgroundColor: '#1c1c1c' }}>
                                <div style={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: '#FF5F56' }} />
                                <div style={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: '#FFBD2E' }} />
                                <div style={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: '#27C93F' }} />
                                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'rgba(244,241,235,0.4)', marginLeft: 10 }}>example.py</span>
                            </div>
                            <pre style={{ padding: '24px 28px', fontFamily: 'var(--font-mono)', fontSize: 13, lineHeight: 1.7, overflowX: 'auto', color: '#F4F1EB' }}>
                                <span style={{ color: '#C586C0' }}>from </span>
                                <span style={{ color: '#B8924A' }}>querymate </span>
                                <span style={{ color: '#C586C0' }}>import </span>
                                <span>QueryMate{'\n\n'}</span>
                                <span style={{ color: '#7A7670' }}># Initialize secure connection{'\n'}</span>
                                <span>qm </span>
                                <span style={{ color: '#C586C0' }}>= </span>
                                <span>QueryMate(db_type</span>
                                <span style={{ color: '#C586C0' }}>=</span>
                                <span style={{ color: '#B8924A' }}>&quot;postgresql&quot;</span>
                                <span>){'\n\n'}</span>
                                <span style={{ color: '#7A7670' }}># Ask in plain English{'\n'}</span>
                                <span>result </span>
                                <span style={{ color: '#C586C0' }}>= </span>
                                <span>qm.ask(</span>
                                <span style={{ color: '#B8924A' }}>&quot;Revenue by merchant?&quot;</span>
                                <span>)</span>
                            </pre>
                        </div>
                    </div>

                </div>

            </div>
        </section>
    )
}

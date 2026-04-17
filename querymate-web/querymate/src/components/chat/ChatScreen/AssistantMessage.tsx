'use client'

import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'

interface Segment {
    content: string
}

interface Props {
    title: string
    segments: Segment[]
    sql?: string
    rowCount?: number
    columns?: string[]
    table?: string
}

export default function AssistantMessage({ title, segments, sql, rowCount, columns, table }: Props) {
    const [sqlOpen, setSqlOpen] = useState(false)
    const [hoverBtn, setHoverBtn] = useState(false)

    return (
        <div style={{ padding: '4px 28px 16px' }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14, marginBottom: 2 }}>

                {/* QM badge */}
                <div style={{
                    flexShrink: 0, width: 32, height: 32,
                    backgroundColor: 'var(--app-gold)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    borderRadius: 2, marginTop: 2,
                }}>
                    <span style={{
                        fontFamily: 'var(--font-space)', fontSize: 11, fontWeight: 700,
                        letterSpacing: '0.08em', color: 'var(--app-ink)',
                    }}>QM</span>
                </div>

                {/* card */}
                <div style={{
                    flex: 1,
                    backgroundColor: 'var(--app-surface)',
                    border: '1px solid var(--app-border)',
                    borderRadius: 4, padding: '20px 22px',
                }}>
                    {/* card header */}
                    <div style={{
                        fontFamily: 'var(--font-space)', fontSize: 9, fontWeight: 700,
                        letterSpacing: '0.16em', color: 'var(--app-text-faint)',
                        textTransform: 'uppercase', marginBottom: 16,
                    }}>
                        {title}
                    </div>

                    {/* paragraphs */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                        {segments.map((s, i) => (
                            <p key={i} style={{
                                fontFamily: 'var(--font-space)', fontSize: 13, fontWeight: 400,
                                color: 'var(--app-text)', lineHeight: 1.75,
                                letterSpacing: '0.01em', margin: 0,
                            }}>
                                {s.content}
                            </p>
                        ))}
                    </div>

                    {/* show sql toggle */}
                    {sql && (
                        <div style={{ marginTop: 20 }}>
                            <button
                                onClick={() => setSqlOpen(v => !v)}
                                onMouseEnter={() => setHoverBtn(true)}
                                onMouseLeave={() => setHoverBtn(false)}
                                style={{
                                    display: 'inline-flex', alignItems: 'center', gap: 6,
                                    fontFamily: 'var(--font-space)', fontSize: 10, fontWeight: 600,
                                    letterSpacing: '0.1em', textTransform: 'uppercase',
                                    color: hoverBtn ? 'var(--app-gold)' : 'var(--app-text-dim)',
                                    border: `1px solid ${hoverBtn ? 'var(--app-border-gold)' : 'var(--app-border)'}`,
                                    padding: '6px 14px', borderRadius: 2,
                                    backgroundColor: hoverBtn ? 'var(--app-gold-dimmer)' : 'transparent',
                                    cursor: 'pointer', transition: 'all 0.15s',
                                }}
                            >
                                {sqlOpen ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
                                Show SQL Query
                            </button>

                            {sqlOpen && (
                                <div style={{
                                    marginTop: 10,
                                    backgroundColor: 'var(--app-surface-deep)',
                                    border: '1px solid var(--app-border)',
                                    borderRadius: 3, padding: '14px 16px', overflowX: 'auto',
                                }}>
                                    <pre style={{
                                        fontFamily: 'var(--font-mono)', fontSize: 12,
                                        color: 'var(--app-gold)',
                                        lineHeight: 1.65, whiteSpace: 'pre-wrap',
                                        wordBreak: 'break-word', margin: 0,
                                    }}>
                                        {sql}
                                    </pre>
                                </div>
                            )}
                        </div>
                    )}

                    {/* metadata footer */}
                    {(rowCount !== undefined || (columns && columns.length > 0)) && (
                        <div style={{
                            marginTop: 18, paddingTop: 14,
                            borderTop: '1px solid var(--app-border-subtle)',
                            display: 'flex', alignItems: 'center', gap: 20, flexWrap: 'wrap',
                        }}>
                            {rowCount !== undefined && table && (
                                <span style={{
                                    fontFamily: 'var(--font-space)', fontSize: 10, fontWeight: 500,
                                    letterSpacing: '0.06em', color: 'var(--app-text-faint)',
                                    display: 'flex', alignItems: 'center', gap: 6, textTransform: 'uppercase',
                                }}>
                                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" style={{ opacity: 0.5 }}>
                                        <rect x="1" y="1" width="10" height="2.5" rx="0.5" fill="var(--app-gold)" />
                                        <rect x="1" y="4.8" width="10" height="2.5" rx="0.5" fill="var(--app-gold)" />
                                        <rect x="1" y="8.5" width="10" height="2.5" rx="0.5" fill="var(--app-gold)" />
                                    </svg>
                                    {rowCount} rows, {columns?.length} columns from {table}
                                </span>
                            )}
                            {columns && columns.length > 0 && (
                                <span style={{
                                    fontFamily: 'var(--font-mono)', fontSize: 10,
                                    color: 'var(--app-text-ghost)',
                                    letterSpacing: '0.04em', display: 'flex', alignItems: 'center', gap: 6,
                                }}>
                                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" style={{ opacity: 0.5 }}>
                                        <rect x="1" y="1" width="2.5" height="10" rx="0.5" fill="var(--app-gold)" />
                                        <rect x="4.8" y="1" width="2.5" height="10" rx="0.5" fill="var(--app-gold)" />
                                        <rect x="8.5" y="1" width="2.5" height="10" rx="0.5" fill="var(--app-gold)" />
                                    </svg>
                                    COLUMNS: {columns.join(', ')}
                                </span>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

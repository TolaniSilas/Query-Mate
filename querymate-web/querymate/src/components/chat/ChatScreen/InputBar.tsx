'use client'

import { useState, useRef, useEffect } from 'react'
import { Database, BarChart2 } from 'lucide-react'

interface Props {
    onSend: (value: string) => void
}

export default function InputBar({ onSend }: Props) {
    const [value, setValue] = useState('')
    const [hover, setHover] = useState(false)
    const textareaRef = useRef<HTMLTextAreaElement>(null)

    // auto-resize
    useEffect(() => {
        const el = textareaRef.current
        if (!el) return
        el.style.height = 'auto'
        el.style.height = Math.min(el.scrollHeight, 120) + 'px'
    }, [value])

    const submit = () => {
        const trimmed = value.trim()
        if (!trimmed) return
        onSend(trimmed)
        setValue('')
    }

    const onKey = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            submit()
        }
    }

    return (
        <div style={{
            padding: '14px 28px 20px',
            borderTop: '1px solid var(--app-border-subtle)',
            backgroundColor: 'var(--app-bg)',
            flexShrink: 0,
        }}>
            <div style={{
                display: 'flex',
                alignItems: 'flex-end',
                gap: 0,
                border: '1px solid var(--app-border-mid)',
                borderRadius: 4,
                backgroundColor: 'var(--app-surface-input)',
                padding: '10px 14px',
                transition: 'border-color 0.15s',
            }}>
                {/* prompt symbol */}
                <span style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: 14,
                    color: 'var(--app-gold)',
                    marginRight: 10,
                    lineHeight: '24px',
                    flexShrink: 0,
                    alignSelf: 'flex-end',
                    marginBottom: 2,
                }}>{'>'}</span>

                {/* textarea */}
                <textarea
                    ref={textareaRef}
                    value={value}
                    onChange={e => setValue(e.target.value)}
                    onKeyDown={onKey}
                    placeholder="Analyze financial architecture..."
                    rows={1}
                    style={{
                        flex: 1,
                        background: 'none',
                        border: 'none',
                        outline: 'none',
                        resize: 'none',
                        fontFamily: 'var(--font-space)',
                        fontSize: 13,
                        color: 'var(--app-text)',
                        lineHeight: '24px',
                        letterSpacing: '0.02em',
                        caretColor: 'var(--app-gold)',
                        overflow: 'hidden',
                    }}
                />

                {/* icon buttons */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginLeft: 12, flexShrink: 0 }}>
                    <button
                        title="Database context"
                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--app-text-ghost)', padding: 4, transition: 'color 0.15s', borderRadius: 2 }}
                        onMouseEnter={e => (e.currentTarget.style.color = 'var(--app-text-dim)')}
                        onMouseLeave={e => (e.currentTarget.style.color = 'var(--app-text-ghost)')}
                    >
                        <Database size={16} strokeWidth={1.5} />
                    </button>
                    <button
                        title="Chart view"
                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--app-text-ghost)', padding: 4, transition: 'color 0.15s', borderRadius: 2 }}
                        onMouseEnter={e => (e.currentTarget.style.color = 'var(--app-text-dim)')}
                        onMouseLeave={e => (e.currentTarget.style.color = 'var(--app-text-ghost)')}
                    >
                        <BarChart2 size={16} strokeWidth={1.5} />
                    </button>

                    {/* query button */}
                    <button
                        onClick={submit}
                        onMouseEnter={() => setHover(true)}
                        onMouseLeave={() => setHover(false)}
                        style={{
                            fontFamily: 'var(--font-space)',
                            fontSize: 11,
                            fontWeight: 700,
                            letterSpacing: '0.1em',
                            textTransform: 'uppercase',
                            color: 'var(--app-ink)',
                            backgroundColor: hover ? 'var(--app-gold-hover)' : 'var(--app-gold)',
                            border: 'none',
                            borderRadius: 2,
                            padding: '6px 16px',
                            cursor: 'pointer',
                            transition: 'background 0.15s',
                        }}
                    >
                        Query
                    </button>
                </div>
            </div>
        </div>
    )
}

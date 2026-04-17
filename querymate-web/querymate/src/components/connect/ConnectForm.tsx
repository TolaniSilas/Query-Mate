'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Database, FolderOpen, Lock, ChevronRight, AlertCircle } from 'lucide-react'

type DbType = 'postgresql' | 'mysql' | 'sqlite'

const DB_TYPES: { id: DbType; label: string; hint: string }[] = [
    {
        id: 'postgresql',
        label: 'PostgreSQL',
        hint: 'postgresql://user:password@host:5432/dbname?sslmode=require',
    },
    {
        id: 'mysql',
        label: 'MySQL',
        hint: 'mysql+pymysql://user:password@host:3306/dbname',
    },
    {
        id: 'sqlite',
        label: 'SQLite',
        hint: '/absolute/path/to/database.db',
    },
]

const STEPS = ['Sign In', 'Connect Database', 'Chat']

const C = {
    root: {
        minHeight: '100vh',
        backgroundColor: 'var(--app-bg)',
        display: 'flex',
        flexDirection: 'column' as const,
        alignItems: 'center',
        justifyContent: 'center',
        padding: '40px 24px',
    },
    logo: {
        fontFamily: "'Playfair Display', Georgia, serif",
        fontSize: 24,
        fontWeight: 600,
        color: 'var(--app-gold)',
        letterSpacing: '-0.02em',
        textDecoration: 'none',
        display: 'block',
        marginBottom: 40,
    },
    card: {
        width: '100%',
        maxWidth: 480,
        backgroundColor: 'var(--app-surface)',
        border: '1px solid var(--app-border)',
        borderRadius: 6,
        padding: '36px 32px 32px',
    },
    stepBar: {
        display: 'flex',
        alignItems: 'center',
        gap: 0,
        marginBottom: 36,
    },
    stepLabel: (active: boolean, done: boolean): React.CSSProperties => ({
        fontFamily: 'var(--font-space)',
        fontSize: 11,
        fontWeight: active ? 600 : 400,
        letterSpacing: '0.08em',
        textTransform: 'uppercase',
        color: active ? 'var(--app-gold)' : done ? 'var(--app-text-muted)' : 'var(--app-text-ghost)',
        whiteSpace: 'nowrap',
    }),
    stepDivider: (done: boolean): React.CSSProperties => ({
        flex: 1,
        height: 1,
        backgroundColor: done ? 'var(--app-border-gold)' : 'var(--app-border-subtle)',
        margin: '0 10px',
    }),
    heading: {
        fontFamily: "'Playfair Display', Georgia, serif",
        fontSize: 22,
        fontWeight: 600,
        color: 'var(--app-text)',
        marginBottom: 6,
        letterSpacing: '-0.01em',
    },
    sub: {
        fontFamily: 'var(--font-space)',
        fontSize: 12,
        color: 'var(--app-text-secondary)',
        marginBottom: 28,
        letterSpacing: '0.02em',
        lineHeight: 1.6,
    },
    label: {
        fontFamily: 'var(--font-space)',
        fontSize: 10,
        fontWeight: 600,
        letterSpacing: '0.1em',
        textTransform: 'uppercase' as const,
        color: 'var(--app-text-secondary)',
        display: 'block',
        marginBottom: 8,
    },
    input: {
        width: '100%',
        padding: '11px 14px',
        backgroundColor: 'var(--app-bg)',
        border: '1px solid var(--app-border-mid)',
        borderRadius: 3,
        color: 'var(--app-text)',
        fontFamily: 'var(--font-mono)',
        fontSize: 12,
        outline: 'none',
        transition: 'border-color 0.15s',
        letterSpacing: '0.03em',
        boxSizing: 'border-box' as const,
    },
    hint: {
        fontFamily: 'var(--font-mono)',
        fontSize: 10,
        color: 'var(--app-text-dim)',
        marginTop: 6,
        letterSpacing: '0.04em',
        lineHeight: 1.5,
    },
    notice: {
        display: 'flex',
        alignItems: 'flex-start',
        gap: 10,
        backgroundColor: 'var(--app-gold-dimmer)',
        border: '1px solid rgba(201,165,90,0.1)',
        borderRadius: 3,
        padding: '10px 14px',
        marginTop: 20,
    },
    noticeText: {
        fontFamily: 'var(--font-space)',
        fontSize: 11,
        color: 'var(--app-text-secondary)',
        lineHeight: 1.65,
        letterSpacing: '0.01em',
    },
    connectBtn: (hover: boolean): React.CSSProperties => ({
        marginTop: 24,
        width: '100%',
        padding: '13px',
        backgroundColor: hover ? 'var(--app-gold-hover)' : 'var(--app-gold)',
        border: 'none',
        borderRadius: 3,
        color: 'var(--app-ink)',
        fontFamily: 'var(--font-space)',
        fontSize: 12,
        fontWeight: 700,
        letterSpacing: '0.1em',
        textTransform: 'uppercase',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 8,
        transition: 'background 0.15s',
    }),
}

export default function ConnectForm() {
    const router = useRouter()
    const [dbType, setDbType] = useState<DbType>('postgresql')
    const [value, setValue] = useState('')
    const [hover, setHover] = useState(false)
    const [focusing, setFocusing] = useState(false)

    const selected = DB_TYPES.find(d => d.id === dbType)!
    const isSQLite = dbType === 'sqlite'

    const handleConnect = () => {
        router.push('/chat')
    }

    return (
        <div style={C.root}>
            {/* logo */}
            <a href="/" style={C.logo}>QueryMate</a>

            <div style={C.card}>
                {/* step indicator */}
                <div style={C.stepBar}>
                    {STEPS.map((step, i) => (
                        <div key={step} style={{ display: 'flex', alignItems: 'center', flex: i < STEPS.length - 1 ? 1 : undefined }}>
                            <span style={C.stepLabel(i === 1, i < 1)}>{step}</span>
                            {i < STEPS.length - 1 && <div style={C.stepDivider(i < 1)} />}
                        </div>
                    ))}
                </div>

                {/* heading */}
                <h1 style={C.heading}>Connect your database</h1>
                <p style={C.sub}>
                    QueryMate needs a connection to your database to answer your questions.
                    Your credentials are used only for this session.
                </p>

                {/* db type tabs */}
                <div style={{ marginBottom: 24 }}>
                    <label style={C.label}>Database type</label>
                    <div style={{
                        display: 'flex',
                        border: '1px solid #1e1a12',
                        borderRadius: 3,
                        overflow: 'hidden',
                    }}>
                        {DB_TYPES.map((db, i) => {
                            const active = db.id === dbType
                            return (
                                <button
                                    key={db.id}
                                    onClick={() => { setDbType(db.id); setValue('') }}
                                    style={{
                                        flex: 1,
                                        padding: '9px 0',
                                        background: active ? 'rgba(201,165,90,0.1)' : 'transparent',
                                        border: 'none',
                                        borderRight: i < DB_TYPES.length - 1 ? '1px solid #1e1a12' : 'none',
                                        color: active ? 'var(--app-gold)' : 'var(--app-text-dim)',
                                        fontFamily: 'var(--font-space)',
                                        fontSize: 11,
                                        fontWeight: active ? 600 : 400,
                                        letterSpacing: '0.06em',
                                        textTransform: 'uppercase',
                                        cursor: 'pointer',
                                        transition: 'all 0.15s',
                                    }}
                                >
                                    {db.label}
                                </button>
                            )
                        })}
                    </div>
                </div>

                {/* connection field */}
                <div>
                    <label style={C.label}>
                        {isSQLite ? (
                            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                                <FolderOpen size={11} strokeWidth={2} style={{ display: 'inline' }} />
                                File path
                            </span>
                        ) : (
                            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                                <Database size={11} strokeWidth={2} style={{ display: 'inline' }} />
                                Database URL
                            </span>
                        )}
                    </label>
                    <input
                        type={isSQLite ? 'text' : 'url'}
                        value={value}
                        onChange={e => setValue(e.target.value)}
                        placeholder={selected.hint}
                        style={{
                            ...C.input,
                            borderColor: focusing ? 'var(--app-border-gold)' : 'var(--app-border-mid)',
                        }}
                        onFocus={() => setFocusing(true)}
                        onBlur={() => setFocusing(false)}
                        autoComplete="off"
                        spellCheck={false}
                    />
                    <p style={C.hint}>
                        {isSQLite
                            ? 'absolute path to your .db or .sqlite file'
                            : 'include credentials in the url — connection is read-only'}
                    </p>
                </div>

                {/* read-only notice */}
                <div style={C.notice}>
                    <Lock size={13} strokeWidth={1.5} style={{ color: 'var(--app-text-faint)', flexShrink: 0, marginTop: 1 }} />
                    <span style={C.noticeText}>
                        QueryMate connects in <strong style={{ color: 'var(--app-gold)' }}>read-only mode</strong>.
                        It can never INSERT, UPDATE, DELETE, or DROP anything in your database.
                        Only SELECT queries are executed.
                    </span>
                </div>

                {/* connect button */}
                <button
                    onClick={handleConnect}
                    onMouseEnter={() => setHover(true)}
                    onMouseLeave={() => setHover(false)}
                    style={C.connectBtn(hover)}
                >
                    Connect and continue
                    <ChevronRight size={14} strokeWidth={2.5} />
                </button>
            </div>

            {/* bottom note */}
            <p style={{
                marginTop: 20,
                fontFamily: 'var(--font-space)',
                fontSize: 11,
                color: 'var(--app-text-dim)',
                letterSpacing: '0.04em',
            }}>
                <AlertCircle size={11} strokeWidth={1.5} style={{ display: 'inline', marginRight: 5, verticalAlign: 'middle', opacity: 0.6 }} />
                Only PostgreSQL, MySQL, and SQLite are supported.
            </p>
        </div>
    )
}

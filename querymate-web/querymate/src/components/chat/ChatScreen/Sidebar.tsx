'use client'

import { useState } from 'react'
import { MessageSquare, Plus, Settings, FileText } from 'lucide-react'

const CONVERSATIONS = [
    { id: '1', label: 'Q3 Revenue Trends', active: true },
    { id: '2', label: 'Debt to Equity FY24' },
    { id: '3', label: 'Tax Anomaly Benelux' },
    { id: '4', label: 'Subsidiary Audit Log' },
    { id: '5', label: 'Q4 Projection Audit' },
    { id: '6', label: 'Compliance Check — EMEA' },
    { id: '7', label: 'Database Latency Report' },
    { id: '8', label: 'User Access Logs' },
]

const S = {
    root: {
        width: 270,
        minWidth: 270,
        height: '100vh',
        backgroundColor: 'var(--app-bg)',
        borderRight: '1px solid var(--app-border)',
        display: 'flex',
        flexDirection: 'column' as const,
        flexShrink: 0,
    },
    top: { padding: '22px 20px 0' },
    logo: {
        fontFamily: "'Playfair Display', Georgia, serif",
        fontSize: 22,
        fontWeight: 600,
        color: 'var(--app-gold)',
        letterSpacing: '-0.02em',
        textDecoration: 'none',
        display: 'block',
        marginBottom: 20,
    },
    status: { marginBottom: 20 },
    statusLabel: {
        fontFamily: 'var(--font-space)',
        fontSize: 9,
        fontWeight: 600,
        letterSpacing: '0.12em',
        color: 'var(--app-text-faint)',
        textTransform: 'uppercase' as const,
        marginBottom: 6,
    },
    statusBadge: {
        display: 'flex',
        alignItems: 'center',
        gap: 7,
        fontFamily: 'var(--font-space)',
        fontSize: 11,
        fontWeight: 500,
        color: 'var(--app-text-secondary)',
        letterSpacing: '0.05em',
    },
    dot: {
        width: 7,
        height: 7,
        borderRadius: '50%',
        backgroundColor: 'var(--app-green)',
        boxShadow: '0 0 6px var(--app-green-glow)',
        flexShrink: 0,
    },
    newChat: {
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        width: '100%',
        padding: '10px 14px',
        border: '1px solid var(--app-border-mid)',
        borderLeft: '3px solid var(--app-gold)',
        borderRadius: 3,
        cursor: 'pointer',
        fontFamily: 'var(--font-space)',
        fontSize: 12,
        fontWeight: 600,
        letterSpacing: '0.08em',
        color: 'var(--app-gold)',
        textTransform: 'uppercase' as const,
        transition: 'background 0.15s',
        marginBottom: 24,
    },
    sectionLabel: {
        fontFamily: 'var(--font-space)',
        fontSize: 9,
        fontWeight: 600,
        letterSpacing: '0.12em',
        color: 'var(--app-text-ghost)',
        textTransform: 'uppercase' as const,
        padding: '0 20px',
        marginBottom: 6,
    },
    convList: {
        flex: 1,
        overflowY: 'auto' as const,
        padding: '0 8px',
    },
    convItem: (active: boolean): React.CSSProperties => ({
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        width: '100%',
        padding: '8px 12px',
        background: active ? 'var(--app-gold-dim)' : 'none',
        border: 'none',
        borderRadius: 3,
        cursor: 'pointer',
        fontFamily: 'var(--font-space)',
        fontSize: 12,
        fontWeight: active ? 500 : 400,
        color: active ? 'var(--app-gold)' : 'var(--app-text-secondary)',
        textAlign: 'left',
        transition: 'all 0.15s',
        letterSpacing: '0.01em',
    }),
    bottom: {
        padding: '12px 12px 20px',
        borderTop: '1px solid var(--app-border-subtle)',
    },
    bottomBtn: {
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        width: '100%',
        padding: '8px 12px',
        background: 'none',
        border: 'none',
        cursor: 'pointer',
        fontFamily: 'var(--font-space)',
        fontSize: 12,
        fontWeight: 500,
        letterSpacing: '0.08em',
        color: 'var(--app-text-muted)',
        textTransform: 'uppercase' as const,
        textAlign: 'left' as const,
        transition: 'color 0.15s',
        borderRadius: 3,
    },
}

export default function Sidebar() {
    const [active, setActive] = useState('1')
    const [hoverNew, setHoverNew] = useState(false)

    return (
        <aside style={S.root}>
            <div style={S.top}>
                {/* logo */}
                <a href="/" style={S.logo}>QueryMate</a>

                {/* status */}
                <div style={S.status}>
                    <div style={S.statusLabel}>System Status</div>
                    <div style={S.statusBadge}>
                        <span style={S.dot} />
                        <span>V2.4.0&#8209;ALPHA &middot; ONLINE</span>
                    </div>
                </div>

                {/* new chat */}
                <button
                    style={{ ...S.newChat, backgroundColor: hoverNew ? 'var(--app-gold-dimmer)' : 'transparent' }}
                    onMouseEnter={() => setHoverNew(true)}
                    onMouseLeave={() => setHoverNew(false)}
                >
                    <Plus size={14} strokeWidth={2.5} />
                    New Chat
                </button>
            </div>

            {/* conversations */}
            <div style={S.sectionLabel}>Recent Conversations</div>
            <div style={S.convList} className="chat-messages">
                {CONVERSATIONS.map(c => (
                    <button
                        key={c.id}
                        style={S.convItem(active === c.id)}
                        onClick={() => setActive(c.id)}
                        onMouseEnter={e => {
                            if (active !== c.id) e.currentTarget.style.color = 'var(--app-text-muted)'
                        }}
                        onMouseLeave={e => {
                            if (active !== c.id) e.currentTarget.style.color = 'var(--app-text-secondary)'
                        }}
                    >
                        <MessageSquare size={13} strokeWidth={1.5} style={{ flexShrink: 0 }} />
                        {c.label}
                    </button>
                ))}
            </div>

            {/* bottom links */}
            <div style={S.bottom}>
                {[
                    { icon: <Settings size={14} strokeWidth={1.5} />, label: 'Settings' },
                    { icon: <FileText size={14} strokeWidth={1.5} />, label: 'Docs' },
                ].map(({ icon, label }) => (
                    <button
                        key={label}
                        style={S.bottomBtn}
                        onMouseEnter={e => (e.currentTarget.style.color = 'var(--app-text-secondary)')}
                        onMouseLeave={e => (e.currentTarget.style.color = 'var(--app-text-muted)')}
                    >
                        {icon}
                        {label}
                    </button>
                ))}
            </div>
        </aside>
    )
}

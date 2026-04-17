'use client'

import { useState, useRef, useEffect } from 'react'
import { Settings, HelpCircle, User } from 'lucide-react'
import Sidebar from '../Sidebar'
import UserMessage from '../UserMessage'
import AssistantMessage from '../AssistantMessage'
import InputBar from '../InputBar'

// mock data types
interface UserMsg { type: 'user'; text: string }
interface AssistantMsg {
    type: 'assistant'
    title: string
    paragraphs: string[]
    sql: string
    rowCount: number
    columns: string[]
    table: string
}
type Message = UserMsg | AssistantMsg

const MOCK_MESSAGES: Message[] = [
    {
        type: 'user',
        text: 'Analyze the Q3 revenue trends for our European subsidiaries',
    },
    {
        type: 'assistant',
        title: 'Intelligence Synthesis: Regional Audit',
        paragraphs: [
            'Analysis of the financial_records cluster reveals a complex revenue architecture for Q3. While aggregate growth remains stable, a granular audit of the subsidiary ledgers indicates a notable 14.2% variance in the DACH-region subsidiary ledger compared to projected forecasts.',
            "Furthermore, we've identified anomalies in the Q3 tax provisioning logic specifically within the Benelux entities, suggesting a potential misalignment between the local statutory reporting and the centralized IFRS consolidation layer.",
        ],
        sql: `SELECT
  s.region,
  s.subsidiary_name,
  SUM(r.revenue_amount)    AS total_revenue,
  SUM(r.projected_amount)  AS projected_revenue,
  ROUND(
    (SUM(r.revenue_amount) - SUM(r.projected_amount))
    / NULLIF(SUM(r.projected_amount), 0) * 100, 2
  )                        AS variance_pct
FROM financial_records r
JOIN subsidiaries s ON s.id = r.subsidiary_id
WHERE r.quarter = 'Q3'
  AND s.region   = 'Europe'
GROUP BY s.region, s.subsidiary_name
ORDER BY variance_pct DESC;`,
        rowCount: 42,
        columns: ['submission_id', 'merchant_id', 'status', 'document_type', 'created_at'],
        table: 'financial_analysis_table',
    },
    {
        type: 'user',
        text: 'Calculate the debt-to-equity ratio for the current fiscal year',
    },
]

export default function ChatScreen() {
    const [messages, setMessages] = useState<Message[]>(MOCK_MESSAGES)
    const endRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages.length])

    const handleSend = (text: string) => {
        setMessages(prev => [...prev, { type: 'user', text }])
        // simulate a thinking response after a tick
        setTimeout(() => {
            setMessages(prev => [
                ...prev,
                {
                    type: 'assistant',
                    title: 'Intelligence Synthesis: Query Result',
                    paragraphs: [
                        'Query received and processed. The requested data has been retrieved from the connected database and analysed.',
                    ],
                    inlineCodes: {},
                    sql: `-- generated SQL\nSELECT * FROM your_table\nWHERE condition = true\nLIMIT 100;`,
                    rowCount: 0,
                    columns: [],
                    table: '',
                },
            ])
        }, 600)
    }

    return (
        <div style={{
            display: 'flex',
            height: '100vh',
            backgroundColor: 'var(--app-bg)',
            overflow: 'hidden',
        }}>
            <Sidebar />

            {/* main area */}
            <div style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                minWidth: 0,
            }}>
                {/* topbar */}
                <div style={{
                    height: 52,
                    borderBottom: '1px solid var(--app-border-subtle)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'flex-end',
                    padding: '0 24px',
                    gap: 6,
                    flexShrink: 0,
                }}>
                    {[
                        { icon: <Settings size={16} strokeWidth={1.5} />, title: 'Settings' },
                        { icon: <HelpCircle size={16} strokeWidth={1.5} />, title: 'Help' },
                    ].map(({ icon, title }) => (
                        <button
                            key={title}
                            title={title}
                            style={{
                                width: 32, height: 32,
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                background: 'none', border: 'none', borderRadius: 3,
                                cursor: 'pointer', color: 'var(--app-text-ghost)',
                                transition: 'color 0.15s',
                            }}
                            onMouseEnter={e => (e.currentTarget.style.color = 'var(--app-text-muted)')}
                            onMouseLeave={e => (e.currentTarget.style.color = 'var(--app-text-ghost)')}
                        >
                            {icon}
                        </button>
                    ))}
                    <div style={{
                        width: 32, height: 32,
                        border: '1px solid var(--app-border-mid)',
                        borderRadius: 3,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        cursor: 'pointer',
                        color: 'var(--app-text-faint)',
                        transition: 'border-color 0.15s',
                    }}
                        onMouseEnter={e => (e.currentTarget.style.borderColor = 'var(--app-border-gold)')}
                        onMouseLeave={e => (e.currentTarget.style.borderColor = 'var(--app-border-mid)')}
                    >
                        <User size={14} strokeWidth={1.5} />
                    </div>
                </div>

                {/* messages */}
                <div
                    className="chat-messages"
                    style={{
                        flex: 1,
                        overflowY: 'auto',
                        padding: '24px 0 8px',
                    }}
                >
                    {messages.map((msg, i) => {
                        if (msg.type === 'user') {
                            return <UserMessage key={i} text={msg.text} />
                        }

                        const am = msg as AssistantMsg
                        return (
                            <AssistantMessage
                                key={i}
                                title={am.title}
                                segments={am.paragraphs.map(p => ({ content: p }))}
                                sql={am.sql}
                                rowCount={am.rowCount}
                                columns={am.columns}
                                table={am.table}
                            />
                        )
                    })}
                    <div ref={endRef} />
                </div>

                <InputBar onSend={handleSend} />
            </div>
        </div>
    )
}

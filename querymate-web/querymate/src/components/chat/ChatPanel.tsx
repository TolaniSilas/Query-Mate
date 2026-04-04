'use client'
import {useState, useRef, useEffect, useCallback} from 'react'
import {X, Send, Database, Loader2, ChevronDown, ChevronRight, AlertCircle, CheckCircle2, PlugZap, Plug, Info} from 'lucide-react'
import type {Message, ConnectionState} from '@/src/types'
import {connectDatabase, disconnectDatabase, sendQuery} from '@/src/lib/api'


interface ChatPanelProps {
  isOpen: boolean
  onClose: () => void
}

const DB_TYPES = ['postgresql', 'mysql', 'sqlite'] as const
type DbType = typeof DB_TYPES[number]

export default function ChatPanel({ isOpen, onClose }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [connection, setConnection] = useState<ConnectionState>({
    connected: false, sessionId: null, dbType: null, tables: [], tableCount: 0,
  })
  const [showForm, setShowForm] = useState(true)
  const [dbType, setDbType] = useState<DbType>('postgresql')
  const [databaseUrl, setDatabaseUrl] = useState('')
  const [sqlitePath, setSqlitePath] = useState('')
  const [connectError, setConnectError] = useState('')
  const [connecting, setConnecting] = useState(false)
  const [expandedSql, setExpandedSql] = useState<Set<string>>(new Set())

  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({behavior: 'smooth'})
  }, [messages, loading])

  useEffect(() => {
    if (isOpen && connection.connected) {
      setTimeout(() => inputRef.current?.focus(), 120)
    }
  }, [isOpen, connection.connected])

  // auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto'
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 120)}px`
    }
  }, [input])

  const handleConnect = async () => {
    setConnectError('')
    setConnecting(true)
    try {
      const result = await connectDatabase(
        dbType,
        dbType !== 'sqlite' ? databaseUrl : '',
        dbType === 'sqlite'  ? sqlitePath  : undefined,
      )
      if (result.status !== 'ok') {
        setConnectError(result.error || 'Connection failed.')
        return
      }
      setConnection({
        connected: true,
        sessionId: result.session_id,
        dbType: result.db_type,
        tables: result.tables ?? [],
        tableCount: result.table_count ?? 0,
      })
      setShowForm(false)
      setMessages([{
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `Connected to your ${result.db_type?.toUpperCase()} database. I can see ${result.table_count} table${(result.table_count ?? 0) !== 1 ? 's' : ''}: ${(result.tables ?? []).join(', ')}. What would you like to know?`,
        timestamp: new Date(),
      }])
    } catch (err) {
      setConnectError(err instanceof Error ? err.message : 'Could not reach the server.')
    } finally {
      setConnecting(false)
    }
  }

  const handleDisconnect = useCallback(async () => {
    if (connection.sessionId) {
      await disconnectDatabase(connection.sessionId).catch(() => {})
    }
    setConnection({ connected: false, sessionId: null, dbType: null, tables: [], tableCount: 0 })
    setShowForm(true)
    setMessages([])
    setDatabaseUrl('')
    setSqlitePath('')
    setConnectError('')
  }, [connection.sessionId])

  const handleSend = async () => {
    const q = input.trim()
    if (!q || loading || !connection.sessionId) return

    setMessages(prev => [...prev, {
      id: crypto.randomUUID(), role: 'user', content: q, timestamp: new Date(),
    }])
    setInput('')
    setLoading(true)

    try {
      const result = await sendQuery(connection.sessionId, q)
      setMessages(prev => [...prev, {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: result.answer  ?? 'No answer returned.',
        sql: result.sql,
        rowCount: result.row_count,
        status: result.status,
        attempts: result.attempts,
        timestamp: new Date(),
      }])
    } catch {
      setMessages(prev => [...prev, {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Could not reach the server. Please check your connection and try again.',
        status: 'error',
        timestamp: new Date(),
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  const toggleSql = (id: string) => {
    setExpandedSql(prev => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  if (!isOpen) return null

  return (
    <>
      {/* backdrop */}
      <div
        onClick={onClose}
        style={{
          position: 'fixed', inset: 0, zIndex: 90,
          backgroundColor: 'rgba(13,13,13,0.4)',
          backdropFilter: 'blur(4px)',
        }}
      />

      {/* panel */}
      <div
        style={{
          position: 'fixed', zIndex: 91,
          bottom: 92, right: 28,
          width: 'min(420px, calc(100vw - 40px))',
          height: 'min(620px, calc(100vh - 120px))',
          backgroundColor: '#111111',
          border: '1px solid rgba(255,255,255,0.09)',
          borderRadius: 8,
          display: 'flex', flexDirection: 'column',
          overflow: 'hidden',
          boxShadow: '0 24px 60px rgba(0,0,0,0.5)',
          animation: 'panelIn 0.25s cubic-bezier(0.22,1,0.36,1)',
        }}
        onClick={e => e.stopPropagation()}
      >
        <style>{`
          @keyframes panelIn {
            from { opacity: 0; transform: translateY(16px) scale(0.97); }
            to   { opacity: 1; transform: translateY(0)   scale(1);    }
          }
          @keyframes dotBounce {
            0%, 80%, 100% { transform: translateY(0);    }
            40%            { transform: translateY(-5px); }
          }
        `}</style>

        {/* ── panel header ── */}
        <div style={{ padding: '12px 14px', borderBottom: '1px solid rgba(255,255,255,0.07)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 28, height: 28, backgroundColor: '#B8924A', borderRadius: 4, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <Database size={13} color="#0D0D0D" strokeWidth={2} />
            </div>
            <div>
              <p style={{ fontFamily: 'var(--font-sans)', fontSize: 13, fontWeight: 500, color: '#F4F1EB', lineHeight: 1.2 }}>QueryMate</p>
              {connection.connected ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 2 }}>
                  <div style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: '#4ade80' }} />
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'rgba(244,241,235,0.38)' }}>
                    {connection.dbType?.toUpperCase()} · {connection.tableCount} tables
                  </span>
                </div>
              ) : (
                <p style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'rgba(244,241,235,0.25)', marginTop: 2 }}>Not connected</p>
              )}
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            {connection.connected && (
              <button
                onClick={handleDisconnect}
                title="Disconnect"
                style={{ display: 'flex', alignItems: 'center', gap: 5, padding: '5px 10px', background: 'none', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 4, cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: 10, color: 'rgba(244,241,235,0.35)', transition: 'all 0.2s' }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.2)'; e.currentTarget.style.color = 'rgba(244,241,235,0.7)' }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)'; e.currentTarget.style.color = 'rgba(244,241,235,0.35)' }}
              >
                <Plug size={10} />
                Disconnect
              </button>
            )}
            <button
              onClick={onClose}
              aria-label="Close"
              style={{ width: 28, height: 28, background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 4, color: 'rgba(244,241,235,0.35)', transition: 'all 0.2s' }}
              onMouseEnter={e => { e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.07)'; e.currentTarget.style.color = '#F4F1EB' }}
              onMouseLeave={e => { e.currentTarget.style.backgroundColor = 'transparent'; e.currentTarget.style.color = 'rgba(244,241,235,0.35)' }}
            >
              <X size={14} />
            </button>
          </div>
        </div>

        {/* ── connect form ── */}
        {showForm && (
          <div style={{ flex: 1, overflowY: 'auto', padding: '20px 18px' }} className="chat-messages">
            <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
              <PlugZap size={15} color="#B8924A" strokeWidth={1.5} style={{ flexShrink: 0, marginTop: 1 }} />
              <div>
                <p style={{ fontFamily: 'var(--font-sans)', fontSize: 13, fontWeight: 500, color: '#F4F1EB', marginBottom: 4 }}>Connect your database</p>
                <p style={{ fontFamily: 'var(--font-sans)', fontSize: 11, color: 'rgba(244,241,235,0.35)', lineHeight: 1.6 }}>
                  Credentials are held server-side only and never returned to the client.
                </p>
              </div>
            </div>

            {/* db type tabs */}
            <div style={{ marginBottom: 16 }}>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'rgba(244,241,235,0.3)', textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: 8 }}>
                Database Type
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 6 }}>
                {DB_TYPES.map(t => (
                  <button
                    key={t}
                    onClick={() => setDbType(t)}
                    style={{
                      padding: '8px 4px', borderRadius: 4, cursor: 'pointer',
                      fontFamily: 'var(--font-mono)', fontSize: 11, transition: 'all 0.15s',
                      backgroundColor: dbType === t ? '#B8924A' : 'rgba(255,255,255,0.04)',
                      color:           dbType === t ? '#0D0D0D'  : 'rgba(244,241,235,0.45)',
                      border:          dbType === t ? '1px solid #B8924A' : '1px solid rgba(255,255,255,0.08)',
                    }}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            {/* url/path field */}
            <div style={{ marginBottom: 16 }}>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'rgba(244,241,235,0.3)', textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: 8 }}>
                {dbType === 'sqlite' ? 'File Path' : 'Database URL'}
              </p>
              <input
                type={dbType !== 'sqlite' ? 'password' : 'text'}
                value={dbType === 'sqlite' ? sqlitePath : databaseUrl}
                onChange={e => dbType === 'sqlite' ? setSqlitePath(e.target.value) : setDatabaseUrl(e.target.value)}
                placeholder={dbType === 'sqlite' ? '/absolute/path/to/db.sqlite' : `${dbType}://user:pass@host/dbname`}
                onKeyDown={e => { if (e.key === 'Enter') handleConnect() }}
                style={{
                  width: '100%', padding: '10px 12px',
                  backgroundColor: 'rgba(255,255,255,0.04)',
                  border: '1px solid rgba(255,255,255,0.09)',
                  borderRadius: 4, outline: 'none',
                  fontFamily: 'var(--font-mono)', fontSize: 12,
                  color: '#F4F1EB',
                }}
                onFocus={e => (e.currentTarget.style.borderColor = 'rgba(184,146,74,0.5)')}
                onBlur={e => (e.currentTarget.style.borderColor  = 'rgba(255,255,255,0.09)')}
              />
            </div>

            {connectError && (
              <div style={{ display: 'flex', gap: 8, padding: '10px 12px', backgroundColor: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 4, marginBottom: 16 }}>
                <AlertCircle size={13} color="#f87171" style={{ flexShrink: 0, marginTop: 1 }} />
                <p style={{ fontFamily: 'var(--font-sans)', fontSize: 12, color: '#f87171', lineHeight: 1.5 }}>{connectError}</p>
              </div>
            )}

            <button
              onClick={handleConnect}
              disabled={connecting || (dbType !== 'sqlite' && !databaseUrl) || (dbType === 'sqlite' && !sqlitePath)}
              style={{
                width: '100%', padding: '11px',
                backgroundColor: '#B8924A', color: '#0D0D0D',
                border: 'none', borderRadius: 4, cursor: 'pointer',
                fontFamily: 'var(--font-sans)', fontSize: 13, fontWeight: 500,
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                transition: 'opacity 0.2s',
                opacity: connecting ? 0.6 : 1,
              }}
              onMouseEnter={e => { if (!connecting) e.currentTarget.style.backgroundColor = '#a67d3f' }}
              onMouseLeave={e => { e.currentTarget.style.backgroundColor = '#B8924A' }}
            >
              {connecting ? <><Loader2 size={14} style={{ animation: 'spin 0.8s linear infinite' }} />Connecting...</> : <><PlugZap size={14} />Connect</>}
            </button>

            <div style={{ marginTop: 16, padding: '10px 12px', backgroundColor: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 4, display: 'flex', gap: 8 }}>
              <Info size={12} color="rgba(244,241,235,0.25)" style={{ flexShrink: 0, marginTop: 1 }} />
              <p style={{ fontFamily: 'var(--font-sans)', fontSize: 11, color: 'rgba(244,241,235,0.3)', lineHeight: 1.6 }}>
                All connections are opened in read-only mode. Write operations are rejected at the connection level.
              </p>
            </div>
          </div>
        )}

        {/* ── messages ── */}
        {!showForm && (
          <div
            className="chat-messages"
            style={{ flex: 1, overflowY: 'auto', padding: '16px 14px', display: 'flex', flexDirection: 'column', gap: 16 }}
          >
            {messages.map(msg => (
              <div key={msg.id} style={{ display: 'flex', flexDirection: 'column', alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>

                {/* bubble */}
                <div
                  style={{
                    maxWidth: '84%',
                    padding: '10px 14px',
                    borderRadius: msg.role === 'user' ? '12px 12px 3px 12px' : '12px 12px 12px 3px',
                    backgroundColor: msg.role === 'user' ? '#B8924A' : 'rgba(255,255,255,0.06)',
                    border: msg.role === 'assistant' ? '1px solid rgba(255,255,255,0.07)' : 'none',
                    fontFamily: 'var(--font-sans)', fontSize: 13,
                    color: msg.role === 'user' ? '#0D0D0D' : 'rgba(244,241,235,0.88)',
                    lineHeight: 1.65,
                  }}
                >
                  {msg.content}
                </div>

                {/* sql toggle */}
                {msg.role === 'assistant' && msg.sql && (
                  <div style={{ maxWidth: '84%', width: '100%', marginTop: 6 }}>
                    <button
                      onClick={() => toggleSql(msg.id)}
                      style={{ display: 'flex', alignItems: 'center', gap: 5, background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: 10, color: 'rgba(244,241,235,0.28)', marginBottom: 4, padding: 0, transition: 'color 0.2s' }}
                      onMouseEnter={e => (e.currentTarget.style.color = 'rgba(244,241,235,0.55)')}
                      onMouseLeave={e => (e.currentTarget.style.color = 'rgba(244,241,235,0.28)')}
                    >
                      {expandedSql.has(msg.id) ? <ChevronDown size={10} /> : <ChevronRight size={10} />}
                      View SQL
                      {msg.rowCount != null && <span style={{ color: 'rgba(244,241,235,0.18)', marginLeft: 4 }}>· {msg.rowCount} row{msg.rowCount !== 1 ? 's' : ''}</span>}
                    </button>
                    {expandedSql.has(msg.id) && (
                      <pre style={{ backgroundColor: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 4, padding: '10px 12px', fontFamily: 'var(--font-mono)', fontSize: 11, color: 'rgba(244,241,235,0.5)', overflowX: 'auto', lineHeight: 1.7, whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                        {msg.sql}
                      </pre>
                    )}
                  </div>
                )}

                {/* meta row */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 4 }}>
                  {msg.role === 'assistant' && msg.status === 'ok' && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      <CheckCircle2 size={10} color="rgba(74,222,128,0.5)" />
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'rgba(244,241,235,0.2)' }}>
                        answered{msg.attempts && msg.attempts > 1 ? ` · ${msg.attempts} attempts` : ''}
                      </span>
                    </div>
                  )}
                  {msg.role === 'assistant' && msg.status && msg.status !== 'ok' && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      <AlertCircle size={10} color="rgba(251,191,36,0.5)" />
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'rgba(244,241,235,0.2)' }}>{msg.status}</span>
                    </div>
                  )}
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'rgba(244,241,235,0.15)' }}>
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>

              </div>
            ))}

            {/* typing indicator */}
            {loading && (
              <div style={{ display: 'flex', alignItems: 'flex-start' }}>
                <div style={{ padding: '12px 16px', backgroundColor: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: '12px 12px 12px 3px', display: 'flex', gap: 5, alignItems: 'center' }}>
                  {[0, 1, 2].map(i => (
                    <div key={i} style={{ width: 5, height: 5, borderRadius: '50%', backgroundColor: 'rgba(244,241,235,0.4)', animation: `dotBounce 1.2s ease ${i * 0.2}s infinite` }} />
                  ))}
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>
        )}

        {/* ── input area ── */}
        {!showForm && (
          <div style={{ padding: '10px 12px', borderTop: '1px solid rgba(255,255,255,0.07)', flexShrink: 0 }}>
            <div
              style={{ display: 'flex', alignItems: 'flex-end', gap: 8, backgroundColor: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, padding: '8px 10px', transition: 'border-color 0.2s' }}
              onFocusCapture={e => (e.currentTarget.style.borderColor = 'rgba(184,146,74,0.4)')}
              onBlurCapture={e  => (e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)')}
            >
              <textarea
                ref={inputRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask a question about your database..."
                rows={1}
                style={{
                  flex: 1, background: 'none', border: 'none', outline: 'none', resize: 'none',
                  fontFamily: 'var(--font-sans)', fontSize: 13, color: '#F4F1EB', lineHeight: 1.5,
                  overflowY: 'hidden',
                }}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || loading}
                aria-label="Send"
                style={{
                  width: 30, height: 30, flexShrink: 0,
                  backgroundColor: input.trim() && !loading ? '#B8924A' : 'rgba(255,255,255,0.07)',
                  border: 'none', borderRadius: 6, cursor: input.trim() ? 'pointer' : 'default',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  transition: 'background 0.2s',
                }}
              >
                {loading
                  ? <Loader2 size={13} color="rgba(244,241,235,0.5)" style={{ animation: 'spin 0.8s linear infinite' }} />
                  : <Send    size={13} color={input.trim() ? '#0D0D0D' : 'rgba(244,241,235,0.25)'} strokeWidth={2} />
                }
              </button>
            </div>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'rgba(244,241,235,0.15)', textAlign: 'center', marginTop: 6 }}>
              Enter to send &nbsp;·&nbsp; Shift+Enter for new line
            </p>
          </div>
        )}

        <style>{`
          @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        `}</style>
      </div>
    </>
  )
}
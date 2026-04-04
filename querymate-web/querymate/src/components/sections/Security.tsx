import { Lock, Search, ShieldCheck, KeyRound, CheckCircle2, Minus, AlertTriangle } from 'lucide-react'

const FEATURES = [
  {
    Icon: Lock,
    title: 'Connection-Level Read-Only',
    desc: 'Read-only is enforced at the database engine level — not application logic. PostgreSQL uses SET SESSION CHARACTERISTICS, MySQL uses SET SESSION TRANSACTION READ ONLY, and SQLite uses file URI mode=ro. Even if all other layers failed, the database itself would still reject write operations.',
  },
  {
    Icon: Search,
    title: 'Rule-Based Query Validation',
    desc: 'query_validator.py performs deterministic keyword scanning before any query reaches the database. It strips SQL comments (line and block), tokenises the query, and rejects anything containing INSERT, UPDATE, DELETE, DROP, TRUNCATE, CREATE, ALTER, and 15 other forbidden keywords. No LLM involved.',
  },
  {
    Icon: ShieldCheck,
    title: 'LLM Semantic Validation',
    desc: 'The Validator Agent is a separate LLM call evaluating SQL across five dimensions: intent alignment, schema correctness, JOIN completeness, logic accuracy, and NULL handling. Rejection returns structured feedback for targeted self-correction — not a generic error.',
  },
  {
    Icon: KeyRound,
    title: 'Secure Credential Handling',
    desc: 'Database credentials are loaded exclusively from environment variables. Only a session_id is returned to the client. The actual connection string, username, and password are held server-side and never exposed through any API response or log output.',
  },
]

const TABLE_ROWS = [
  { feature: 'Read-only connection enforcement',      qm: true,  lc: false },
  { feature: 'Rule-based SQL keyword scanning',       qm: true,  lc: false },
  { feature: 'LLM semantic validation gate',          qm: true,  lc: 'opt' },
  { feature: 'Agentic retry loop with feedback',      qm: true,  lc: false },
  { feature: 'Credentials never returned to client',  qm: true,  lc: false },
  { feature: 'Comment stripping before scan',         qm: true,  lc: false },
]

function Cell({ value }: { value: boolean | string }) {
  if (value === true)    return <CheckCircle2  size={16} color="#B8924A" strokeWidth={2} />
  if (value === 'opt')   return <AlertTriangle size={16} color="#d97706" strokeWidth={2} />
  return <Minus size={14} color="rgba(122,118,112,0.4)" strokeWidth={2} />
}

export default function Security() {
  return (
    <section id="security" style={{ padding: '112px 0', backgroundColor: '#EFECEA' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 32px' }}>

        {/* header */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '32px 64px', marginBottom: 64 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
              <div style={{ height: 1, width: 32, backgroundColor: '#B8924A' }} />
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: '#B8924A', textTransform: 'uppercase', letterSpacing: '0.15em' }}>Security</span>
            </div>
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(36px, 5vw, 56px)', fontWeight: 400, lineHeight: 1.05, color: '#0D0D0D', letterSpacing: '-0.02em' }}>
              Security is not
              <br /><em>optional here.</em>
            </h2>
          </div>
          <p style={{ fontFamily: 'var(--font-sans)', fontSize: 15, color: '#7A7670', lineHeight: 1.75, display: 'flex', alignItems: 'flex-end' }}>
            Most Text-to-SQL tools delegate security entirely to the developer.
            QueryMate enforces it at every layer — automatically — so your database
            is protected by default, not by convention.
          </p>
        </div>

        {/* feature cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16, marginBottom: 48 }}>
          {FEATURES.map(({ Icon, title, desc }) => (
            <div
              key={title}
              style={{ backgroundColor: '#F4F1EB', border: '1px solid #E8E3D8', borderRadius: 3, padding: '28px 24px', transition: 'border-color 0.2s' }}
              onMouseEnter={e => (e.currentTarget.style.borderColor = '#B8924A')}
              onMouseLeave={e => (e.currentTarget.style.borderColor = '#E8E3D8')}
            >
              <div style={{ display: 'flex', gap: 16 }}>
                <div style={{ width: 36, height: 36, border: '1px solid #E8E3D8', borderRadius: 3, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <Icon size={14} color="#7A7670" strokeWidth={1.5} />
                </div>
                <div>
                  <h3 style={{ fontFamily: 'var(--font-sans)', fontSize: 14, fontWeight: 600, color: '#0D0D0D', marginBottom: 8 }}>{title}</h3>
                  <p style={{ fontFamily: 'var(--font-sans)', fontSize: 13, color: '#7A7670', lineHeight: 1.75 }}>{desc}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* comparison table */}
        <div style={{ backgroundColor: '#F4F1EB', border: '1px solid #E8E3D8', borderRadius: 3, overflow: 'hidden' }}>
          <div style={{ padding: '14px 24px', borderBottom: '1px solid #E8E3D8', backgroundColor: '#EFECEA', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: '#7A7670', textTransform: 'uppercase', letterSpacing: '0.12em' }}>QueryMate vs LangChain SQL Toolkit</p>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: '#B8B3AA' }}>Security comparison</p>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #E8E3D8' }}>
                  <th style={{ textAlign: 'left', padding: '12px 24px', fontFamily: 'var(--font-mono)', fontSize: 10, color: '#7A7670', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 400 }}>Feature</th>
                  <th style={{ textAlign: 'center', padding: '12px 24px', fontFamily: 'var(--font-mono)', fontSize: 10, color: '#B8924A', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 400 }}>QueryMate</th>
                  <th style={{ textAlign: 'center', padding: '12px 24px', fontFamily: 'var(--font-mono)', fontSize: 10, color: '#7A7670', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 400 }}>LangChain</th>
                </tr>
              </thead>
              <tbody>
                {TABLE_ROWS.map(({ feature, qm, lc }, i) => (
                  <tr key={feature} style={{ borderBottom: i < TABLE_ROWS.length - 1 ? '1px solid #E8E3D8' : 'none' }}>
                    <td style={{ padding: '14px 24px', fontFamily: 'var(--font-sans)', fontSize: 13, color: '#0D0D0D' }}>{feature}</td>
                    <td style={{ padding: '14px 24px', textAlign: 'center' }}><div style={{ display: 'flex', justifyContent: 'center' }}><Cell value={qm} /></div></td>
                    <td style={{ padding: '14px 24px', textAlign: 'center' }}><div style={{ display: 'flex', justifyContent: 'center' }}><Cell value={lc} /></div></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={{ padding: '12px 24px', borderTop: '1px solid #E8E3D8', display: 'flex', flexWrap: 'wrap', gap: '8px 24px' }}>
            {[
              { Icon: CheckCircle2,  color: '#B8924A', label: 'Built-in'      },
              { Icon: AlertTriangle, color: '#d97706', label: 'Optional add-on' },
              { Icon: Minus,         color: '#B8B3AA', label: 'Not available'  },
            ].map(({ Icon, color, label }) => (
              <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <Icon size={12} color={color} strokeWidth={2} />
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: '#7A7670' }}>{label}</span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </section>
  )
}
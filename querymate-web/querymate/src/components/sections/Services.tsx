 'use client'

import { useScrollReveal } from '@/src/components/utils/useScrollReveal'
import { Languages, Shield, Brain, RefreshCw, ShieldCheck, Database, Eye } from 'lucide-react'

const SERVICES = [
  { Icon: Languages, n: '01', title: 'Natural Language Translation', tag: 'SQL Agent', desc: 'The SQL Agent converts plain English questions into precise, dialect-specific SQL queries with full schema context. Supports PostgreSQL, MySQL, and SQLite syntax.' },
  { Icon: Shield, n: '02', title: 'Guardrails', tag: 'Input Security', desc: 'Guardrails screen prompts for unsafe instructions, out-of-policy requests, and missing context before any downstream token generation begins, reducing risk and controlling LLM cost.' },
  { Icon: Brain, n: '03', title: 'LLM-Based Semantic Validation', tag: 'Validator Agent', desc: 'A dedicated Validator Agent evaluates generated SQL across five dimensions: semantic alignment, schema correctness, JOIN completeness, logic accuracy, and edge case handling.' },
  { Icon: RefreshCw, n: '04', title: 'Agentic Retry Loop', tag: 'Pipeline', desc: 'When validation fails, structured feedback passes back to the SQL Agent for targeted self-correction. The system retries up to three times without regenerating from scratch.' },
  { Icon: ShieldCheck, n: '05', title: 'Layered Security Enforcement', tag: 'Security', desc: 'Two independent layers: a rule-based keyword scanner rejects non-SELECT queries, and read-only is enforced at the connection level before any LLM output can cause harm.' },
  { Icon: Database, n: '06', title: 'Schema Understanding via ORM', tag: 'Schema Inspector', desc: 'SQLAlchemy inspects your database at connection time — capturing tables, columns, types, primary keys, foreign keys, and sample rows. Cached and injected into every agent call.' },
  { Icon: Eye, n: '07', title: 'Human-Readable Responses', tag: 'Response Agent',  desc: 'The Response Agent synthesises raw query results into natural language insights — totals, trends, comparisons. Raw rows and SQL are never exposed to non-technical users.' },
]

export default function Services() {
  const rootRef = useScrollReveal<HTMLDivElement>()

  return (
    <section id="services" style={{ padding: '112px 0', backgroundColor: '#0D0D0D' }}>
      <div ref={rootRef} style={{ maxWidth: 1200, margin: '0 auto', padding: '0 32px' }}>

        {/* header */}
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'flex-end', justifyContent: 'space-between', gap: '24px 48px', marginBottom: 64 }}>
          <div>
            <div data-scroll-reveal className="scroll-reveal delay-100" style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
              <div style={{ height: 1, width: 32, backgroundColor: '#B8924A' }} />
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: '#B8924A', textTransform: 'uppercase', letterSpacing: '0.15em' }}>What it does</span>
            </div>
            <h2 data-scroll-reveal className="scroll-reveal delay-200" style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(36px, 5vw, 56px)', fontWeight: 400, lineHeight: 1.05, color: '#F4F1EB', letterSpacing: '-0.02em' }}>
              Seven Steps - Security First.
              <br /><em style={{ color: '#B8924A' }}>One Answer.</em>
            </h2>
          </div>
          <p data-scroll-reveal className="scroll-reveal delay-300" style={{ fontFamily: 'var(--font-sans)', fontSize: 13, color: 'rgba(244,241,235,0.4)', maxWidth: 320, lineHeight: 1.7 }}>
            Each service is a discrete, independently testable component in the pipeline — from your question to a precise answer.
          </p>
        </div>

        {/* grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: 1,
            backgroundColor: 'rgba(255,255,255,0.06)',
          }}
        >
          {SERVICES.map(({ Icon, n, title, tag, desc }, idx) => (
            <div
              key={n}
              data-scroll-reveal
              className={`scroll-reveal delay-${Math.min(700, (idx + 1) * 100)}`}
              style={{ backgroundColor: '#0D0D0D', padding: '36px 32px', transition: 'background 0.25s' }}
              onMouseEnter={e => (e.currentTarget.style.backgroundColor = '#161616')}
              onMouseLeave={e => (e.currentTarget.style.backgroundColor = '#0D0D0D')}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 28 }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'rgba(244,241,235,0.2)' }}>{n}</span>
                <div style={{ width: 36, height: 36, border: '1px solid rgba(255,255,255,0.08)', borderRadius: 3, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Icon size={14} color="rgba(244,241,235,0.35)" strokeWidth={1.5} />
                </div>
              </div>
              <h3 style={{ fontFamily: 'var(--font-sans)', fontSize: 15, fontWeight: 500, color: '#F4F1EB', marginBottom: 12, lineHeight: 1.4 }}>{title}</h3>
              <p style={{ fontFamily: 'var(--font-sans)', fontSize: 13, color: 'rgba(244,241,235,0.38)', lineHeight: 1.75, marginBottom: 24 }}>{desc}</p>
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, padding: '4px 10px', backgroundColor: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 100 }}>
                <div style={{ width: 4, height: 4, borderRadius: '50%', backgroundColor: '#B8924A' }} />
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'rgba(244,241,235,0.35)' }}>{tag}</span>
              </div>
            </div>
          ))}
        </div>

      </div>
    </section>
  )
}

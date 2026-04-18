 'use client'

import { ArrowRight } from 'lucide-react'
import { useScrollReveal } from '@/src/components/utils/useScrollReveal'

const STEPS = [
  { n: '01', label: 'User Question', desc: 'A natural-language question enters through the web app or API.', dark: false },
  { n: '02', label: 'Guardrails', desc: 'Input rules screen for unsafe instructions, unsupported requests, and missing context before SQL is generated.', dark: false },
  { n: '03', label: 'SQL Agent', desc: 'The model generates dialect-aware SQL using schema context, table relationships, and the user intent.', dark: true },
  { n: '04', label: 'Validator Agent', desc: 'A second pass checks semantic fit, schema alignment, joins, filters, and whether the query actually answers the question.', dark: true },
  { n: '05', label: 'Security Gate', desc: 'Deterministic checks block non-SELECT statements, dangerous patterns, and anything outside the read-only policy.', dark: false },
  { n: '06', label: 'DB Execution', desc: 'Only approved SQL executes against the connected database in a read-only session.', dark: false },
  { n: '07', label: 'Response Agent', desc: 'Structured results are translated into a concise answer with business-facing wording and no hidden side effects.', dark: true },
]

const LAYERS = [
  {
    label: 'Connection Layer',
    items: ['SQLite file URI mode=ro', 'PostgreSQL SESSION READ ONLY', 'MySQL SESSION READ ONLY'],
  },
  {
    label: 'Application Layer',
    items: ['Guardrails for unsafe prompts and out-of-policy requests', 'Keyword token scanning', 'SQL comment stripping', 'Dangerous function blocking'],
  },
  {
    label: 'Agent Layer',
    items: ['Validator Agent (LLM)', 'SQL Agent retry loop', 'Response synthesis'],
  },
]

export default function Architecture() {
  const rootRef = useScrollReveal<HTMLDivElement>()

  return (
    <section id="architecture" style={{ padding: '112px 0', backgroundColor: '#F4F1EB' }}>
      <div ref={rootRef} style={{ maxWidth: 1200, margin: '0 auto', padding: '0 32px' }}>

        {/* section header */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '32px 64px', marginBottom: 64 }}>
          <div>
            <div data-scroll-reveal className="scroll-reveal delay-100" style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
              <div style={{ height: 1, width: 32, backgroundColor: '#B8924A' }} />
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: '#B8924A', textTransform: 'uppercase', letterSpacing: '0.15em' }}>System Design & Architecture</span>
            </div>
            <h2 data-scroll-reveal className="scroll-reveal delay-200" style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(36px, 5vw, 56px)', fontWeight: 400, lineHeight: 1.05, color: '#0D0D0D', letterSpacing: '-0.02em' }}>
              How it
              <br /><em>actually works.</em>
            </h2>
          </div>
          <p data-scroll-reveal className="scroll-reveal delay-300" style={{ fontFamily: 'var(--font-sans)', fontSize: 15, color: '#7A7670', lineHeight: 1.75, display: 'flex', alignItems: 'flex-end' }}>
            A multi-agent pipeline where each stage has a single responsibility.
            The system is designed so that every layer can fail independently
            without exposing your database to risk.
          </p>
        </div>

        {/* pipeline label */}
        <p data-scroll-reveal className="scroll-reveal delay-400" style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: '#7A7670', textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: 20 }}>
          Pipeline Flow
        </p>

        {/* pipeline steps — horizontal scroll on small screens */}
        <div data-scroll-reveal className="scroll-reveal delay-500" style={{ display: 'flex', alignItems: 'stretch', gap: 2, marginBottom: 48, overflowX: 'auto', paddingBottom: 4 }}>
          {STEPS.map(({ n, label, desc, dark }, i) => (
            <div key={n} style={{ display: 'flex', alignItems: 'center', flexShrink: 0, flex: '1 1 150px', minWidth: 130 }}>
              <div
                style={{
                  flex: 1,
                  padding: '20px 18px',
                  backgroundColor: dark ? '#0D0D0D' : '#F4F1EB',
                  border: `1px solid ${dark ? '#2a2a2a' : '#E8E3D8'}`,
                  borderRadius: 3,
                  height: '100%',
                  minHeight: 160,
                }}
              >
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: dark ? 'rgba(244,241,235,0.25)' : '#B8B3AA', display: 'block', marginBottom: 12 }}>{n}</span>
                <p style={{ fontFamily: 'var(--font-sans)', fontSize: 13, fontWeight: 500, color: dark ? '#F4F1EB' : '#0D0D0D', marginBottom: 8, lineHeight: 1.3 }}>{label}</p>
                <p style={{ fontFamily: 'var(--font-sans)', fontSize: 11, color: dark ? 'rgba(244,241,235,0.4)' : '#7A7670', lineHeight: 1.6 }}>{desc}</p>
              </div>
              {i < STEPS.length - 1 && (
                <ArrowRight size={12} color="#B8B3AA" strokeWidth={1.5} style={{ flexShrink: 0, margin: '0 4px' }} />
              )}
            </div>
          ))}
        </div>

        {/* security layers table */}
        <div data-scroll-reveal className="scroll-reveal delay-600" style={{ border: '1px solid #E8E3D8', borderRadius: 3, overflow: 'hidden', marginBottom: 32 }}>
          <div style={{ padding: '14px 24px', borderBottom: '1px solid #E8E3D8', backgroundColor: '#EFECEA' }}>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: '#7A7670', textTransform: 'uppercase', letterSpacing: '0.12em' }}>
              Security Layers
            </p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', borderTop: 'none' }}>
            {LAYERS.map((layer, li) => (
              <div
                key={layer.label}
                style={{
                  padding: '24px',
                  borderRight: li < LAYERS.length - 1 ? '1px solid #E8E3D8' : 'none',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
                  <div style={{ width: 4, height: 4, borderRadius: '50%', backgroundColor: '#B8924A' }} />
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: '#7A7670', textTransform: 'uppercase', letterSpacing: '0.1em' }}>{layer.label}</span>
                </div>
                <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {layer.items.map(item => (
                    <li key={item} style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
                      <ArrowRight size={11} color="#B8924A" strokeWidth={2} style={{ flexShrink: 0, marginTop: 2 }} />
                      <span style={{ fontFamily: 'var(--font-sans)', fontSize: 13, color: '#0D0D0D', lineHeight: 1.5 }}>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* pull quote */}
        <div data-scroll-reveal className="scroll-reveal delay-700" style={{ backgroundColor: '#0D0D0D', borderRadius: 3, padding: '28px 32px', display: 'flex', gap: 20 }}>
          <div style={{ width: 3, flexShrink: 0, backgroundColor: '#B8924A', borderRadius: 2 }} />
          <div>
            <p style={{ fontFamily: 'var(--font-display)', fontSize: 20, fontStyle: 'italic', color: '#F4F1EB', marginBottom: 8 }}>
              &ldquo;A multi-agent Text-to-SQL system with an agentic retry loop.&rdquo;
            </p>
            <p style={{ fontFamily: 'var(--font-sans)', fontSize: 13, color: 'rgba(244,241,235,0.4)' }}>
              The SQL Agent self-corrects based on structured feedback from the Validator Agent before execution.
            </p>
          </div>
        </div>

      </div>
    </section>
  )
}

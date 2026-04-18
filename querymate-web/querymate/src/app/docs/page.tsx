import Link from 'next/link'
import type { Metadata } from 'next'
import type { CSSProperties } from 'react'
import { ArrowLeft, ArrowUpRight, BookOpen, GitBranch, Shield, Terminal } from 'lucide-react'
import Footer from '@/src/components/layout/Footer'

export const metadata: Metadata = {
  title: 'QueryMate Docs',
  description: 'Documentation for the QueryMate Python package, including installation, usage, contribution guidance, and future direction.',
}

const sectionTitleStyle: CSSProperties = {
  fontFamily: 'var(--font-display)',
  fontSize: 'clamp(28px, 4vw, 42px)',
  fontWeight: 400,
  color: '#0D0D0D',
  letterSpacing: '-0.02em',
  lineHeight: 1.1,
  marginBottom: 16,
}

const cardStyle: CSSProperties = {
  backgroundColor: '#F9F7F2',
  border: '1px solid #E8E3D8',
  borderRadius: 8,
  padding: 28,
}

const monoLabelStyle: CSSProperties = {
  fontFamily: 'var(--font-mono)',
  fontSize: 11,
  color: '#B8924A',
  textTransform: 'uppercase',
  letterSpacing: '0.14em',
}

export default function DocsPage() {
  return (
    <>
      <main style={{ minHeight: '100vh', backgroundColor: '#F4F1EB', color: '#0D0D0D' }}>
        <section style={{ borderBottom: '1px solid #E8E3D8', background: 'linear-gradient(180deg, #F9F7F2 0%, #F4F1EB 100%)' }}>
          <div style={{ maxWidth: 1200, margin: '0 auto', padding: '28px 32px 88px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 16, flexWrap: 'wrap', marginBottom: 56 }}>
              <Link
                href="/"
                className="font-space"
                style={{ display: 'inline-flex', alignItems: 'center', gap: 10, color: '#7A7670', textDecoration: 'none', fontSize: 14, fontWeight: 500 }}
              >
                <ArrowLeft size={16} />
                Back to Site
              </Link>

              <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                <a
                  href="https://pypi.org/project/query-mate/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-space"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: 10, backgroundColor: '#0D0D0D', color: '#F4F1EB', padding: '12px 18px', borderRadius: 4, textDecoration: 'none', fontSize: 14, fontWeight: 600 }}
                >
                  <ArrowUpRight size={15} />
                  View on PyPI
                </a>
                <a
                  href="https://github.com/TolaniSilas/Query-Mate/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-space"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: 10, backgroundColor: '#EFE7D8', color: '#0D0D0D', padding: '12px 18px', borderRadius: 4, textDecoration: 'none', fontSize: 14, fontWeight: 600, border: '1px solid #E1D5BF' }}
                >
                  <GitBranch size={15} />
                  Contribute on GitHub
                </a>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.1fr) minmax(280px, 0.9fr)', gap: '40px 56px', alignItems: 'end' }}>
              <div>
                <p style={{ ...monoLabelStyle, marginBottom: 20 }}>Documentation</p>
                <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(48px, 8vw, 84px)', fontWeight: 400, color: '#0D0D0D', letterSpacing: '-0.03em', lineHeight: 0.95, marginBottom: 24 }}>
                  QueryMate
                  <br />
                  <em style={{ color: '#B8924A', fontStyle: 'italic' }}>Python package docs.</em>
                </h1>
                <p style={{ maxWidth: 720, fontSize: 17, color: '#7A7670', lineHeight: 1.75 }}>
                  QueryMate gives Python applications a secure natural-language layer for relational databases.
                  This page covers installation, package usage, operational requirements, contribution workflow,
                  and the direction the project is moving toward.
                </p>
              </div>

              <div style={{ ...cardStyle, backgroundColor: '#0D0D0D', borderColor: '#1F1B16' }}>
                <p style={{ ...monoLabelStyle, color: '#B8924A', marginBottom: 14 }}>Quick Install</p>
                <pre style={{ fontFamily: 'var(--font-mono)', fontSize: 14, color: '#F4F1EB', lineHeight: 1.8, overflowX: 'auto' }}>
                  pip install querymate
                </pre>
                <p style={{ fontSize: 13, color: 'rgba(244,241,235,0.58)', lineHeight: 1.7, marginTop: 14 }}>
                  Python 3.10+, PostgreSQL, MySQL, and SQLite support. QueryMate also expects
                  a memory database and Redis for session-aware conversations.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section style={{ padding: '88px 0' }}>
          <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 32px', display: 'grid', gridTemplateColumns: 'minmax(0, 0.75fr) minmax(0, 1.25fr)', gap: '40px 56px' }}>
            <aside style={{ position: 'sticky', top: 24, alignSelf: 'start' }}>
              <div style={{ ...cardStyle, padding: 24 }}>
                <p style={{ ...monoLabelStyle, marginBottom: 16 }}>On This Page</p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {[
                    ['overview', 'Overview'],
                    ['quick-start', 'Quick Start'],
                    ['requirements', 'Requirements'],
                    ['api', 'Public API'],
                    ['security', 'Security Model'],
                    ['contributing', 'Contributing'],
                    ['roadmap', 'Future Direction'],
                  ].map(([href, label]) => (
                    <a key={href} href={`#${href}`} style={{ textDecoration: 'none', color: '#7A7670', fontSize: 14 }}>
                      {label}
                    </a>
                  ))}
                </div>
              </div>
            </aside>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
              <section id="overview" style={cardStyle}>
                <p style={{ ...monoLabelStyle, marginBottom: 14 }}>Overview</p>
                <h2 style={sectionTitleStyle}>What QueryMate is for</h2>
                <p style={{ fontSize: 15, color: '#4B4742', lineHeight: 1.85 }}>
                  QueryMate is a natural-language interface for relational databases that developers can embed
                  into backend systems. It translates plain-English questions into SQL, validates the result,
                  executes only approved read-only queries, and returns a human-readable answer. It is aimed at
                  internal tools, analyst workflows, stakeholder-facing assistants, and products where non-SQL users
                  still need trustworthy access to structured data.
                </p>
              </section>

              <section id="quick-start" style={cardStyle}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14 }}>
                  <Terminal size={16} color="#B8924A" />
                  <p style={monoLabelStyle}>Quick Start</p>
                </div>
                <h2 style={sectionTitleStyle}>Use the package in a backend service</h2>
                <p style={{ fontSize: 15, color: '#4B4742', lineHeight: 1.85, marginBottom: 18 }}>
                  The main entry point is the <code>QueryMate</code> class. Create one instance per connected user
                  session, ask a plain-English question, then read the structured result.
                </p>
                <pre style={{ backgroundColor: '#161616', borderRadius: 6, padding: '22px 24px', overflowX: 'auto', color: '#F4F1EB', fontFamily: 'var(--font-mono)', fontSize: 13, lineHeight: 1.8 }}>
{`from querymate import QueryMate

qm = QueryMate(
    user_id="user_abc123",
    database_url="postgresql://user:password@host/dbname?sslmode=require",
    db_type="postgresql",
)

result = qm.ask("which merchant had the highest revenue last month?")

print(result.answer)
print(result.sql)
print(result.rows)
print(result.status)

qm.disconnect()`}
                </pre>
                <p style={{ fontSize: 14, color: '#7A7670', lineHeight: 1.75, marginTop: 18 }}>
                  For SQLite, provide <code>sqlite_path</code> instead of <code>database_url</code>. The returned
                  result object exposes <code>answer</code>, <code>sql</code>, <code>rows</code>, <code>row_count</code>,
                  <code>attempts</code>, <code>status</code>, and <code>error</code>.
                </p>
              </section>

              <section id="requirements" style={cardStyle}>
                <p style={{ ...monoLabelStyle, marginBottom: 14 }}>Requirements</p>
                <h2 style={sectionTitleStyle}>Operational setup</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
                  {[
                    {
                      title: 'Supported databases',
                      text: 'PostgreSQL, MySQL, and SQLite are currently supported by the package and the site copy.',
                    },
                    {
                      title: 'Memory services',
                      text: 'Conversation state depends on MEMORY_DATABASE_URL and REDIS_URL so follow-up questions remain grounded.',
                    },
                    {
                      title: 'Python runtime',
                      text: 'The project targets Python 3.10+ according to the package metadata.',
                    },
                  ].map((item) => (
                    <div key={item.title} style={{ backgroundColor: '#F4F1EB', border: '1px solid #E8E3D8', borderRadius: 6, padding: 18 }}>
                      <h3 style={{ fontSize: 14, fontWeight: 600, color: '#0D0D0D', marginBottom: 8 }}>{item.title}</h3>
                      <p style={{ fontSize: 13, color: '#7A7670', lineHeight: 1.7 }}>{item.text}</p>
                    </div>
                  ))}
                </div>
              </section>

              <section id="api" style={cardStyle}>
                <p style={{ ...monoLabelStyle, marginBottom: 14 }}>Public API</p>
                <h2 style={sectionTitleStyle}>The developer-facing surface area</h2>
                <div style={{ display: 'grid', gap: 14 }}>
                  {[
                    'QueryMate(user_id, db_type, database_url=None, sqlite_path=None) opens a secured database session and caches schema context.',
                    'ask(question) runs the full pipeline and returns a QueryResult object with answer, SQL, rows, status, attempt count, and error fields.',
                    'disconnect() closes the active database and memory session cleanly and should be called when the user session ends.',
                  ].map((line) => (
                    <div key={line} style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                      <BookOpen size={15} color="#B8924A" style={{ flexShrink: 0, marginTop: 4 }} />
                      <p style={{ fontSize: 15, color: '#4B4742', lineHeight: 1.8 }}>{line}</p>
                    </div>
                  ))}
                </div>
              </section>

              <section id="security" style={cardStyle}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14 }}>
                  <Shield size={16} color="#B8924A" />
                  <p style={monoLabelStyle}>Security Model</p>
                </div>
                <h2 style={sectionTitleStyle}>How safety is enforced</h2>
                <p style={{ fontSize: 15, color: '#4B4742', lineHeight: 1.85, marginBottom: 18 }}>
                  QueryMate is designed with layered defenses rather than a single safety check. Guardrails validate
                  user input before expensive generation happens. SQL then passes through semantic validation and
                  deterministic rule-based validation before the database sees it. Read-only behavior is enforced at
                  the engine or session level, so the system does not rely on application logic alone to prevent writes.
                </p>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
                  {[
                    ['Prompt guardrails', 'Unsafe instructions, out-of-policy prompts, and missing context are screened early to reduce risk and control token cost.'],
                    ['Semantic validation', 'A dedicated validator checks intent alignment, schema correctness, joins, logic, and edge cases before execution.'],
                    ['Read-only enforcement', 'Connection-level controls and SELECT-only validation protect the database even if another layer misbehaves.'],
                  ].map(([title, text]) => (
                    <div key={title} style={{ backgroundColor: '#F4F1EB', border: '1px solid #E8E3D8', borderRadius: 6, padding: 18 }}>
                      <h3 style={{ fontSize: 14, fontWeight: 600, color: '#0D0D0D', marginBottom: 8 }}>{title}</h3>
                      <p style={{ fontSize: 13, color: '#7A7670', lineHeight: 1.7 }}>{text}</p>
                    </div>
                  ))}
                </div>
              </section>

              <section id="contributing" style={cardStyle}>
                <p style={{ ...monoLabelStyle, marginBottom: 14 }}>Contributing</p>
                <h2 style={sectionTitleStyle}>How contributions are welcome</h2>
                <p style={{ fontSize: 15, color: '#4B4742', lineHeight: 1.85, marginBottom: 18 }}>
                  Contributions are a great fit for this project. Useful areas include database support, validation
                  improvements, documentation, developer ergonomics, frontend polish, tests, and performance work.
                  Good contributions usually start with a focused issue or proposal, a small scoped branch, and test
                  coverage for behavior changes.
                </p>
                <pre style={{ backgroundColor: '#161616', borderRadius: 6, padding: '18px 22px', overflowX: 'auto', color: '#F4F1EB', fontFamily: 'var(--font-mono)', fontSize: 13, lineHeight: 1.8 }}>
{`uv run pytest tests/ -v
uv run pytest tests/querymate/ -v
uv run pytest tests/api/ -v`}
                </pre>
              </section>

              <section id="roadmap" style={cardStyle}>
                <p style={{ ...monoLabelStyle, marginBottom: 14 }}>Future Direction</p>
                <h2 style={sectionTitleStyle}>Where the package can grow</h2>
                <div style={{ display: 'grid', gap: 14 }}>
                  {[
                    'Stronger packaging and release polish so the Python distribution, docs, and installation story are fully aligned.',
                    'Richer developer integration patterns for APIs, workers, and long-lived application sessions.',
                    'Broader observability around retries, validation outcomes, latency, and query safety decisions.',
                    'Expanded database support and more configurable policy layers for enterprise deployments.',
                  ].map((line) => (
                    <p key={line} style={{ fontSize: 15, color: '#4B4742', lineHeight: 1.8 }}>
                      {line}
                    </p>
                  ))}
                </div>
              </section>
            </div>
          </div>
        </section>
      </main>

      <Footer />

      <style>{`
        @media (max-width: 960px) {
          main section > div {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </>
  )
}

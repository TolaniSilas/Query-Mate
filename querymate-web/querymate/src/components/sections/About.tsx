import { Users, BarChart3, FileSearch, MessageSquare } from 'lucide-react'

const USE_CASES = [
  { Icon: Users,       title: 'Non-Technical Stakeholders', desc: 'Executives and analysts query databases directly in plain English — no SQL knowledge required at any level.' },
  { Icon: BarChart3,   title: 'Business Intelligence',      desc: 'Rapid reporting and data exploration through a conversational interface that understands business context.' },
  { Icon: FileSearch,  title: 'Data Exploration',           desc: 'Explore unfamiliar schemas quickly by asking natural questions about structure, relationships, and content.' },
  { Icon: MessageSquare, title: 'Database Documentation',   desc: 'Understand database schemas through natural language queries rather than reading raw DDL definitions.' },
]

export default function About() {
  return (
    <section id="about" style={{ padding: '112px 0', backgroundColor: '#F4F1EB' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 32px' }}>

        {/* header grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '48px 64px', marginBottom: 72 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
              <div style={{ height: 1, width: 32, backgroundColor: '#B8924A' }} />
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: '#B8924A', textTransform: 'uppercase', letterSpacing: '0.15em' }}>About the Project</span>
            </div>
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(36px, 5vw, 56px)', fontWeight: 400, lineHeight: 1.05, color: '#0D0D0D', letterSpacing: '-0.02em' }}>
              Databases speak SQL.
              <br /><em style={{ fontStyle: 'italic' }}>You don&apos;t have to.</em>
            </h2>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}>
            <p style={{ fontFamily: 'var(--font-sans)', fontSize: 15, color: '#7A7670', lineHeight: 1.75, marginBottom: 16 }}>
              QueryMate is a natural language Python package and interface for relational databases.
              It currently supports MySQL, PostgreSQL, and SQLite, and enforces security at both
              the connection level and query level — ensuring only safe, read-only operations
              reach your database.
            </p>
            <p style={{ fontFamily: 'var(--font-sans)', fontSize: 15, color: '#7A7670', lineHeight: 1.75 }}>
              Built around a multi-agent pipeline, it translates natural language questions into
              validated SQL, executes them safely, and returns precise human-readable answers.
            </p>
          </div>
        </div>

        {/* divider */}
        <div style={{ height: 1, backgroundColor: '#E8E3D8', marginBottom: 64 }} />

        {/* use cases */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '40px 32px', marginBottom: 64 }}>
          {USE_CASES.map(({ Icon, title, desc }) => (
            <div key={title}>
              <div style={{ width: 40, height: 40, border: '1px solid #E8E3D8', borderRadius: 3, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 20 }}>
                <Icon size={16} color="#7A7670" strokeWidth={1.5} />
              </div>
              <h3 style={{ fontFamily: 'var(--font-sans)', fontSize: 14, fontWeight: 600, color: '#0D0D0D', marginBottom: 8 }}>{title}</h3>
              <p style={{ fontFamily: 'var(--font-sans)', fontSize: 13, color: '#7A7670', lineHeight: 1.7 }}>{desc}</p>
            </div>
          ))}
        </div>

        {/* database strip */}
        <div style={{ paddingTop: 32, borderTop: '1px solid #E8E3D8', display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '12px 24px' }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: '#7A7670', textTransform: 'uppercase', letterSpacing: '0.12em' }}>Supported databases</span>
          <div style={{ width: 1, height: 16, backgroundColor: '#E8E3D8' }} />
          {['PostgreSQL', 'MySQL', 'SQLite'].map(db => (
            <div key={db} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 5, height: 5, borderRadius: '50%', backgroundColor: '#B8924A' }} />
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 13, color: '#0D0D0D' }}>{db}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
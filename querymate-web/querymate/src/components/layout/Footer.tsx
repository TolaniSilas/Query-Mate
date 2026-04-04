import { Database, Package, BookOpen, ArrowUpRight } from 'lucide-react'

const COLS = [
  {
    heading: 'Product',
    links: [
      { label: 'About',        href: '#about'        },
      { label: 'Services',     href: '#services'     },
      { label: 'Architecture', href: '#architecture' },
      { label: 'Security',     href: '#security'     },
    ],
  },
  {
    heading: 'Developers',
    links: [
      { label: 'Documentation', href: '#', ext: true },
      { label: 'PyPI Package',  href: '#', ext: true },
      // { label: 'GitHub',        href: '#', ext: true },
      { label: 'Changelog',     href: '#', ext: true },
    ],
  },
  {
    heading: 'Databases',
    links: [
      { label: 'PostgreSQL', href: '#' },
      { label: 'MySQL',      href: '#' },
      { label: 'SQLite',     href: '#' },
    ],
  },
]

export default function Footer() {
  return (
    <footer style={{ backgroundColor: '#0D0D0D', color: '#F4F1EB' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '64px 32px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '48px 32px' }}>

          {/* brand */}
          <div style={{ gridColumn: 'span 1' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
              <div style={{ width: 30, height: 30, backgroundColor: '#B8924A', borderRadius: 3, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Database size={14} color="#0D0D0D" strokeWidth={1.5} />
              </div>
              <span style={{ fontFamily: 'var(--font-display)', fontSize: 17, fontWeight: 500 }}>
                Query<span style={{ color: '#B8924A' }}>Mate</span>
              </span>
            </div>
            <p style={{ fontFamily: 'var(--font-sans)', fontSize: 13, color: 'rgba(244,241,235,0.45)', lineHeight: 1.7, maxWidth: 220, marginBottom: 24 }}>
              A natural language Python package and interface for relational databases.
            </p>
            <div style={{ display: 'flex', gap: 16 }}>
              {[
                // { Icon: Github,   label: 'GitHub',        href: '#' },
                { Icon: Package,  label: 'PyPI',          href: '#' },
                { Icon: BookOpen, label: 'Documentation', href: '#' },
              ].map(({ Icon, label, href }) => (
                <a
                  key={label}
                  href={href}
                  aria-label={label}
                  style={{ color: 'rgba(244,241,235,0.35)', transition: 'color 0.2s', display: 'flex' }}
                  onMouseEnter={e => (e.currentTarget.style.color = '#B8924A')}
                  onMouseLeave={e => (e.currentTarget.style.color = 'rgba(244,241,235,0.35)')}
                >
                  <Icon size={17} />
                </a>
              ))}
            </div>
          </div>

          {/* link columns */}
          {COLS.map(col => (
            <div key={col.heading}>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'rgba(244,241,235,0.3)', textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: 18 }}>
                {col.heading}
              </p>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 12 }}>
                {col.links.map(link => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      target={(link as { ext?: boolean }).ext ? '_blank' : undefined}
                      rel={(link as { ext?: boolean }).ext ? 'noopener noreferrer' : undefined}
                      style={{ fontFamily: 'var(--font-sans)', fontSize: 13, color: 'rgba(244,241,235,0.45)', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 4, transition: 'color 0.2s' }}
                      onMouseEnter={e => (e.currentTarget.style.color = '#F4F1EB')}
                      onMouseLeave={e => (e.currentTarget.style.color = 'rgba(244,241,235,0.45)')}
                    >
                      {link.label}
                      {(link as { ext?: boolean }).ext && <ArrowUpRight size={11} />}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          {/* install block */}
          <div>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'rgba(244,241,235,0.3)', textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: 18 }}>
              Install
            </p>
            <div style={{ backgroundColor: '#1e1e1e', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 4, padding: '12px 14px' }}>
              <code style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: '#B8924A' }}>
                pip install querymate
              </code>
            </div>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'rgba(244,241,235,0.2)', marginTop: 10 }}>
              Python 3.10+
            </p>
          </div>
        </div>
      </div>

      {/* bottom bar */}
      <div style={{ borderTop: '1px solid rgba(255,255,255,0.07)' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '18px 32px', display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
          <p style={{ fontFamily: 'var(--font-sans)', fontSize: 12, color: 'rgba(244,241,235,0.25)' }}>
            &copy; {new Date().getFullYear()} QueryMate. Open source under MIT License.
          </p>
          <div style={{ display: 'flex', gap: 24 }}>
            {['Privacy', 'Terms', 'License'].map(l => (
              <a key={l} href="#" style={{ fontFamily: 'var(--font-sans)', fontSize: 12, color: 'rgba(244,241,235,0.25)', textDecoration: 'none', transition: 'color 0.2s' }}
                onMouseEnter={e => (e.currentTarget.style.color = 'rgba(244,241,235,0.6)')}
                onMouseLeave={e => (e.currentTarget.style.color = 'rgba(244,241,235,0.25)')}
              >{l}</a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  )
}
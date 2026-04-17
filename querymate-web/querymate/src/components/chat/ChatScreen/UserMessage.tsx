'use client'

interface Props {
    text: string
}

export default function UserMessage({ text }: Props) {
    return (
        <div style={{
            display: 'flex',
            justifyContent: 'flex-end',
            alignItems: 'flex-start',
            gap: 12,
            padding: '12px 28px',
        }}>
            <p style={{
                fontFamily: 'var(--font-space)',
                fontSize: 13,
                fontWeight: 400,
                color: 'var(--app-text)',
                lineHeight: 1.6,
                maxWidth: 640,
                textAlign: 'right',
                letterSpacing: '0.02em',
            }}>
                {text}
            </p>
            <div style={{
                flexShrink: 0,
                width: 38,
                height: 26,
                border: '1px solid var(--app-border-gold)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: 2,
            }}>
                <span style={{
                    fontFamily: 'var(--font-space)',
                    fontSize: 10,
                    fontWeight: 700,
                    letterSpacing: '0.1em',
                    color: 'var(--app-gold)',
                }}>USR</span>
            </div>
        </div>
    )
}

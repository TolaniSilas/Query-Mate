import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title:       'QueryMate — Natural Language for Relational Databases',
  description: 'QueryMate is a natural language Python package for querying relational databases. Supports MySQL, PostgreSQL, and SQLite with enforced read-only security.',
  keywords:    ['text-to-sql', 'natural language', 'database', 'postgresql', 'llm', 'querymate'],
  openGraph: {
    title:       'QueryMate',
    description: 'Ask questions in plain English. Get answers from your database.',
    type:        'website',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
      </head>
      <body>{children}</body>
    </html>
  )
}
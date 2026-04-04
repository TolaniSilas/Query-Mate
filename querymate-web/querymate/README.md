# QueryMate Web

Production Next.js frontend for the QueryMate Text-to-SQL system.

## Setup

```bash
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Lucide React icons
- IBM Plex Sans + Playfair Display fonts

## Structure

```
src/
  app/              # Next.js App Router (layout, page, globals.css)
  components/
    layout/         # Header, Footer
    sections/       # Hero, About, Services, Architecture, Security
    chat/           # ChatButton, ChatPanel
  lib/              # api.ts — backend client
  types/            # shared TypeScript types
```

## Environment Variables

| Variable                | Description                        | Default                    |
|-------------------------|------------------------------------|----------------------------|
| `NEXT_PUBLIC_API_URL`   | URL of the QueryMate FastAPI server | `http://localhost:8000`   |
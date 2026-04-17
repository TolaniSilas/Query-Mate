import { useEffect, useRef } from 'react'

export function useScrollReveal<T extends HTMLElement = HTMLDivElement>() {
  const rootRef = useRef<T | null>(null)

  useEffect(() => {
    const root = rootRef.current
    if (!root) return

    const items = Array.from(root.querySelectorAll<HTMLElement>('[data-scroll-reveal]'))
    if (items.length === 0) return

    const prefersReducedMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    if (prefersReducedMotion) {
      for (const el of items) el.classList.remove('scroll-reveal')
      return
    }

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue
          const el = entry.target as HTMLElement
          el.classList.remove('scroll-reveal')
          el.classList.add('reveal-up')
          observer.unobserve(el)
        }
      },
      { threshold: 0.15, rootMargin: '0px 0px -10% 0px' }
    )

    for (const el of items) observer.observe(el)
    return () => observer.disconnect()
  }, [])

  return rootRef
}

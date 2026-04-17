'use client'

import { useRouter } from 'next/navigation'
import Header from '@/src/components/layout/Header'
import Footer from '@/src/components/layout/Footer'
import Hero from '@/src/components/sections/Hero'
import About from '@/src/components/sections/About'
import Services from '@/src/components/sections/Services'
import Architecture from '@/src/components/sections/Architecture'
import Security from '@/src/components/sections/Security'
import ChatButton from '@/src/components/chat/ChatButton'
import Package from '@/src/components/sections/Package'

export default function Home() {
  const router = useRouter()
  const goToChat = () => router.push('/signup')

  return (
    <>
      <Header onTryChat={goToChat} />

      <main>
        <Hero />
        <div style={{ position: 'relative', zIndex: 10, backgroundColor: 'var(--paper)' }}>
          <About />
          <Package />
          <Services />
          <Architecture />
          <Security />
        </div>
      </main>

      <Footer />

      <ChatButton
        isOpen={false}
        onClick={goToChat}
      />
    </>
  )
}
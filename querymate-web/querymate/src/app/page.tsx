'use client'

import { useState } from 'react'
import Header from '@/src/components/layout/Header'
import Footer from '@/src/components/layout/Footer'
import Hero from '@/src/components/sections/Hero'
import About from '@/src/components/sections/About'
import Services from '@/src/components/sections/Services'
import Architecture from '@/src/components/sections/Architecture'
import Security from '@/src/components/sections/Security'
import ChatButton from '@/src/components/chat/ChatButton'
// import ChatPanel from '@/src/components/chat/ChatPanel'

export default function Home() {
  const [chatOpen, setChatOpen] = useState(false)

  return (
    <>
      <Header />

      <main>
        <Hero />
        <About />
        <Services />
        <Architecture />
        <Security />
      </main>

      <Footer />

      <ChatButton
        isOpen={chatOpen}
        onClick={() => setChatOpen(prev => !prev)}
      />
      {/* <ChatPanel
        isOpen={chatOpen}
        onClose={() => setChatOpen(false)}
      /> */}
    </>
  )
}
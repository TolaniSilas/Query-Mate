import Header from '@/src/components/layout/Header'
import Footer from '@/src/components/layout/Footer'
import AuthSection from '@/src/components/auth/AuthSection'

export default function SignInPage() {
  return (
    <>
      <Header />
      <main>
        <div
          style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            paddingTop: 120,
            paddingBottom: 80,
            paddingLeft: 32,
            paddingRight: 32,
          }}
        >
          <AuthSection mode="signin" />
        </div>
      </main>
      <Footer />
    </>
  )
}

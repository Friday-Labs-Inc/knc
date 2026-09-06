import type { ReactNode } from 'react'
import Nav from './Nav'
import Footer from './Footer'

// Shared page chrome — fixed nav, the page body (cleared below the 60px nav),
// and the footer. Every marketing page wraps in this.
export default function Layout({ children }: { children: ReactNode }) {
  return (
    <>
      <Nav />
      <main className="pt-[60px]">{children}</main>
      <Footer />
    </>
  )
}

import { useLocation } from 'react-router-dom'
import Nav from '../components/Nav'
import Wizard from '../wizard/Wizard'

// /start — the onboarding wizard. The hero input bar passes its text in via
// router state, pre-filling "what you do".
export default function Start() {
  const location = useLocation()
  const intro = (location.state as { intro?: string } | null)?.intro

  return (
    <>
      <Nav />
      <main className="mx-auto min-h-screen max-w-narrow px-5 pb-24 pt-[120px] md:px-8">
        <Wizard intro={intro} />
      </main>
    </>
  )
}

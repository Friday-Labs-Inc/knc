import { FrappeProvider } from 'frappe-react-sdk'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './routes/Home'
import Work from './routes/Work'
import CaseStudy from './routes/CaseStudy'
import Services from './routes/Services'
import About from './routes/About'
import Journal from './routes/Journal'
import ArticlePost from './routes/ArticlePost'
import Contact from './routes/Contact'
import Start from './routes/Start'
import Login from './routes/Login'
import Portal from './routes/Portal'

// Served under /frontend for now (the catch-all website rule handles sub-paths,
// so every route below works). Clean URLs (/, /work, …) are a later polish —
// flip this to '/' then.
const BASENAME = '/frontend'

export default function App() {
  return (
    <FrappeProvider>
      <BrowserRouter basename={BASENAME}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/work" element={<Work />} />
          <Route path="/work/:slug" element={<CaseStudy />} />
          <Route path="/services" element={<Services />} />
          <Route path="/about" element={<About />} />
          <Route path="/journal" element={<Journal />} />
          <Route path="/journal/:slug" element={<ArticlePost />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/start" element={<Start />} />
          <Route path="/login" element={<Login />} />
          <Route path="/portal/*" element={<Portal />} />
        </Routes>
      </BrowserRouter>
    </FrappeProvider>
  )
}

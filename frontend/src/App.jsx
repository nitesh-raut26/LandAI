import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import BackendHealthBanner from './components/BackendHealthBanner'
import Footer from './components/Footer'
import Home from './pages/Home'
import CityAnalysis from './pages/CityAnalysis'
import Compare from './pages/Compare'
import Analytics from './pages/Analytics'

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <BackendHealthBanner />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/city" element={<Navigate to="/" replace />} />
        <Route path="/city/:cityId" element={<CityAnalysis />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <Footer />
    </BrowserRouter>
  )
}

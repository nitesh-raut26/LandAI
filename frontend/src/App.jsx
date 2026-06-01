import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import BackendHealthBanner from './components/BackendHealthBanner'
import Footer from './components/Footer'
import Home from './pages/Home'
import CityAnalysis from './pages/CityAnalysis'
import Compare from './pages/Compare'
import Analytics from './pages/Analytics'
import Login from './pages/Login'
import Register from './pages/Register'
import Account from './pages/Account'
import ApiKeys from './pages/ApiKeys'
import Dashboard from './pages/Dashboard'
import Usage from './pages/Usage'
import Docs from './pages/Docs'

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
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/account" element={<Account />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/usage" element={<Usage />} />
        <Route path="/keys" element={<ApiKeys />} />
        <Route path="/docs" element={<Docs />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <Footer />
    </BrowserRouter>
  )
}

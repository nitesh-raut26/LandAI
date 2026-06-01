import React from 'react'
import ReactDOM from 'react-dom/client'
import 'leaflet/dist/leaflet.css'
import App from './App'
import { DataTrustProvider } from './context/DataTrustContext'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <DataTrustProvider>
      <App />
    </DataTrustProvider>
  </React.StrictMode>
)

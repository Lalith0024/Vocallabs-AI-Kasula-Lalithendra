import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import NewCampaign from './pages/NewCampaign';
import CampaignDetail from './pages/CampaignDetail';
import { ToastProvider } from './components/Toast';

function App() {
  return (
    <ToastProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-slate-900 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(59,130,246,0.15),rgba(255,255,255,0))]">
          <Navbar />
          <main>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/campaigns/new" element={<NewCampaign />} />
              <Route path="/campaigns/:id" element={<CampaignDetail />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </ToastProvider>
  );
}

export default App;

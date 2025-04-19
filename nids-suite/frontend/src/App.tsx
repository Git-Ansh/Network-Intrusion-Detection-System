import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';
import AlertsPage from './pages/AlertsPage';
import NetworkMapPage from './pages/NetworkMapPage';
import PacketExplorerPage from './pages/PacketExplorerPage';
import LoginPage from './pages/LoginPage';
import SettingsPage from './pages/SettingsPage';
import { AuthProvider } from './contexts/AuthContext';
import { SocketProvider } from './contexts/SocketContext';
import DashboardLayout from './components/dashboard/DashboardLayout';

const App = () => {
  return (
    <AuthProvider>
      <SocketProvider>
        <Router>
          <DashboardLayout>
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/alerts" element={<AlertsPage />} />
              <Route path="/network-map" element={<NetworkMapPage />} />
              <Route path="/packet-explorer" element={<PacketExplorerPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </DashboardLayout>
        </Router>
      </SocketProvider>
    </AuthProvider>
  );
};

export default App;
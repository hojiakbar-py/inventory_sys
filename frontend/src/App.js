import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, useLocation } from 'react-router-dom';
import './App.css';
import Dashboard from './components/Dashboard';
import Equipment from './components/Equipment';
import EquipmentDetail from './components/EquipmentDetail';
import Employees from './components/Employees';
import EmployeeDetail from './components/EmployeeDetail';
import QRCodes from './components/QRCodes';
import QRScanner from './components/QRScanner';
import InvoiceScanner from './components/InvoiceScanner';
import History from './components/History';
import Login from './components/Login';
import Register from './components/Register';
import Profile from './components/Profile';
import ProtectedRoute from './components/ProtectedRoute';

// Main App Component with Sidebar
function MainApp() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  // Close sidebar when route changes (mobile)
  useEffect(() => {
    setSidebarOpen(false);
  }, [location]);

  // Close sidebar when clicking outside (mobile)
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (window.innerWidth <= 768 && sidebarOpen) {
        if (!e.target.closest('.sidebar') && !e.target.closest('.mobile-menu-toggle')) {
          setSidebarOpen(false);
        }
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [sidebarOpen]);

  return (
    <div className="App">
      {/* Mobile Menu Toggle */}
      <button
        className="mobile-menu-toggle"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        aria-label="Toggle menu"
      >
        {sidebarOpen ? '✕' : '☰'}
      </button>

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <h2>Inventarizatsiya</h2>
        <nav>
          <ul>
            <li>
              <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''}>
                📊 Boshqaruv paneli
              </NavLink>
            </li>
            <li>
              <NavLink to="/equipment" className={({ isActive }) => isActive ? 'active' : ''}>
                💻 Qurilmalar
              </NavLink>
            </li>
            <li>
              <NavLink to="/employees" className={({ isActive }) => isActive ? 'active' : ''}>
                👥 Hodimlar
              </NavLink>
            </li>
            <li>
              <NavLink to="/qr-codes" className={({ isActive }) => isActive ? 'active' : ''}>
                📱 QR Kodlar
              </NavLink>
            </li>
            <li>
              <NavLink to="/qr-scanner" className={({ isActive }) => isActive ? 'active' : ''}>
                🔍 QR Skaner
              </NavLink>
            </li>
            <li>
              <NavLink to="/invoice-scanner" className={({ isActive }) => isActive ? 'active' : ''}>
                📄 Nakladnoy Scanner
              </NavLink>
            </li>
            <li>
              <NavLink to="/history" className={({ isActive }) => isActive ? 'active' : ''}>
                📅 Tarix
              </NavLink>
            </li>
            <li>
              <NavLink to="/profile" className={({ isActive }) => isActive ? 'active' : ''}>
                👤 Profil
              </NavLink>
            </li>
          </ul>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/equipment" element={<Equipment />} />
          <Route path="/equipment/:id" element={<EquipmentDetail />} />
          <Route path="/employees" element={<Employees />} />
          <Route path="/employee/:id" element={<EmployeeDetail />} />
          <Route path="/qr-codes" element={<QRCodes />} />
          <Route path="/qr-scanner" element={<QRScanner />} />
          <Route path="/invoice-scanner" element={<InvoiceScanner />} />
          <Route path="/history" element={<History />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes - No Sidebar/Auth required for viewing via QR */}
        <Route path="/equipment/:id" element={<EquipmentDetail />} />
        <Route path="/employee/:id" element={<EmployeeDetail />} />

        {/* Auth Routes - No Sidebar */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Main App Routes - With Sidebar */}
        <Route path="/*" element={
          <ProtectedRoute>
            <MainApp />
          </ProtectedRoute>
        } />
      </Routes>
    </Router>
  );
}

export default App;

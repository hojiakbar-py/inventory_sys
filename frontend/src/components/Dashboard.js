import React, { useState, useEffect } from 'react';
import { assignmentAPI } from '../api';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardStats();
  }, []);

  const loadDashboardStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await assignmentAPI.getDashboardStats();
      setStats(response.data);
    } catch (error) {
      console.error('Statistikani yuklashda xatolik:', error);
      setError(error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner size="large" text="Dashboard yuklanmoqda..." />;
  }

  if (error) {
    return <ErrorMessage error={error} onRetry={loadDashboardStats} />;
  }

  return (
    <div>
      <div className="page-header">
        <h1>Boshqaruv Paneli</h1>
        <p>Inventarizatsiya tizimi umumiy ko'rinishi</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Jami qurilmalar</h3>
          <div className="value">{stats?.total_equipment || 0}</div>
        </div>
        <div className="stat-card">
          <h3>Mavjud qurilmalar</h3>
          <div className="value" style={{color: '#27ae60'}}>{stats?.available_equipment || 0}</div>
        </div>
        <div className="stat-card">
          <h3>Tayinlangan</h3>
          <div className="value" style={{color: '#3498db'}}>{stats?.assigned_equipment || 0}</div>
        </div>
        <div className="stat-card warning">
          <h3>Ta'mirlashda</h3>
          <div className="value">{stats?.maintenance_equipment || 0}</div>
        </div>
        <div className="stat-card">
          <h3>Hodimlar</h3>
          <div className="value">{stats?.total_employees || 0}</div>
        </div>
        <div className="stat-card">
          <h3>Bo'limlar</h3>
          <div className="value">{stats?.total_departments || 0}</div>
        </div>
      </div>

      <div className="data-table">
        <div className="table-header">
          <h2>So'nggi Tayinlashlar</h2>
        </div>
        <div className="table-wrapper">
          <table>
          <thead>
            <tr>
              <th>Qurilma</th>
              <th>Hodim</th>
              <th>Tayinlangan sana</th>
              <th>Holati</th>
            </tr>
          </thead>
          <tbody>
            {stats?.recent_assignments?.length > 0 ? (
              stats.recent_assignments.map((assignment) => (
                <tr key={assignment.id}>
                  <td>{assignment.equipment_name}</td>
                  <td>{assignment.employee_name}</td>
                  <td>{new Date(assignment.assigned_date).toLocaleDateString('uz-UZ')}</td>
                  <td>
                    {assignment.return_date ? (
                      <span className="badge badge-success">Qaytarilgan</span>
                    ) : (
                      <span className="badge badge-warning">Foydalanishda</span>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4" style={{ textAlign: 'center' }}>
                  Hozircha tayinlashlar yo'q
                </td>
              </tr>
            )}
          </tbody>
        </table>
        </div>
      </div>

      <div className="data-table" style={{marginTop: '30px'}}>
        <div className="table-header">
          <h2>So'nggi Inventarizatsiya Tekshiruvlari</h2>
        </div>
        <div className="table-wrapper">
          <table>
          <thead>
            <tr>
              <th>Qurilma</th>
              <th>Sana</th>
              <th>Tekshirgan</th>
              <th>Holati</th>
            </tr>
          </thead>
          <tbody>
            {stats?.recent_checks?.length > 0 ? (
              stats.recent_checks.map((check) => (
                <tr key={check.id}>
                  <td>{check.equipment_name}</td>
                  <td>{new Date(check.check_date).toLocaleDateString('uz-UZ')}</td>
                  <td>{check.checked_by_name || 'N/A'}</td>
                  <td>
                    {check.is_functional ? (
                      <span className="badge badge-success">Ishlayapti</span>
                    ) : (
                      <span className="badge badge-danger">Ishlamayapti</span>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4" style={{ textAlign: 'center' }}>
                  Hozircha tekshiruvlar yo'q
                </td>
              </tr>
            )}
          </tbody>
        </table>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

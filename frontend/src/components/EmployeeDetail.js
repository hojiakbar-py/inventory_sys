import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { employeeAPI } from '../api';

function EmployeeDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [employee, setEmployee] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadEmployee();
  }, [id]);

  const loadEmployee = async () => {
    try {
      // id employee_id yoki database ID bo'lishi mumkin
      const response = await employeeAPI.getAll({ search: id });

      if (response.data.results && response.data.results.length > 0) {
        setEmployee(response.data.results[0]);
      } else if (response.data && response.data.length > 0) {
        setEmployee(response.data[0]);
      } else {
        setError('Hodim topilmadi');
      }

      setLoading(false);
    } catch (error) {
      console.error('Hodimni yuklashda xatolik:', error);
      setError('Hodimni yuklashda xatolik yuz berdi');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h2>Yuklanmoqda...</h2>
      </div>
    );
  }

  if (error || !employee) {
    return (
      <div style={{ padding: '20px' }}>
        <h2 style={{ color: '#d32f2f' }}>❌ Xatolik</h2>
        <p>{error || 'Hodim topilmadi'}</p>
        <button
          className="btn btn-primary"
          onClick={() => navigate('/employees')}
          style={{ marginTop: '20px' }}
        >
          Hodimlar ro'yxatiga qaytish
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: 'clamp(10px, 3vw, 20px)' }}>
      <div className="page-header">
        <h1 style={{ fontSize: 'clamp(1.5rem, 5vw, 2rem)' }}>
          👤 {employee.full_name}
        </h1>
        <button
          className="btn btn-primary"
          onClick={() => navigate('/employees')}
          style={{ marginTop: '10px' }}
        >
          ← Orqaga
        </button>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '20px',
        marginTop: '20px'
      }}>
        {/* Shaxsiy ma'lumotlar */}
        <div style={{
          backgroundColor: '#f5f5f5',
          padding: 'clamp(15px, 3vw, 25px)',
          borderRadius: '10px',
          border: '3px solid #2196f3'
        }}>
          <h3 style={{
            color: '#1976d2',
            marginBottom: '15px',
            fontSize: 'clamp(1.1rem, 3.5vw, 1.3rem)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            👤 Shaxsiy Ma'lumotlar
          </h3>
          <div style={{ fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>
            <p style={{ marginBottom: '10px' }}>
              <strong>F.I.O:</strong><br/>
              <span style={{ fontSize: 'clamp(1rem, 3vw, 1.2rem)', color: '#1976d2' }}>
                {employee.full_name}
              </span>
            </p>
            <p style={{ marginBottom: '10px' }}>
              <strong>Hodim ID:</strong><br/>
              <span style={{
                padding: '4px 10px',
                backgroundColor: '#e3f2fd',
                borderRadius: '6px',
                fontFamily: 'monospace',
                fontWeight: 'bold'
              }}>
                {employee.employee_id}
              </span>
            </p>
            <p style={{ marginBottom: '10px' }}>
              <strong>Lavozim:</strong><br/>{employee.position}
            </p>
            <p style={{ marginBottom: '10px' }}>
              <strong>Bo'lim:</strong><br/>{employee.department_name || 'N/A'}
            </p>
            <p style={{ marginBottom: 0 }}>
              <strong>Holat:</strong><br/>
              <span style={{
                padding: '4px 12px',
                borderRadius: '15px',
                backgroundColor: employee.is_active ? '#4caf50' : '#f44336',
                color: 'white',
                fontWeight: 'bold'
              }}>
                {employee.is_active ? 'Faol' : 'Nofaol'}
              </span>
            </p>
          </div>
        </div>

        {/* Aloqa ma'lumotlari */}
        <div style={{
          backgroundColor: '#f5f5f5',
          padding: 'clamp(15px, 3vw, 25px)',
          borderRadius: '10px',
          border: '3px solid #4caf50'
        }}>
          <h3 style={{
            color: '#388e3c',
            marginBottom: '15px',
            fontSize: 'clamp(1.1rem, 3.5vw, 1.3rem)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            📞 Aloqa Ma'lumotlari
          </h3>
          <div style={{ fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>
            <p style={{ marginBottom: '10px', wordBreak: 'break-all' }}>
              <strong>Email:</strong><br/>
              {employee.email ? (
                <a href={`mailto:${employee.email}`} style={{ color: '#1976d2' }}>
                  {employee.email}
                </a>
              ) : 'N/A'}
            </p>
            <p style={{ marginBottom: '10px' }}>
              <strong>Telefon:</strong><br/>
              {employee.phone ? (
                <a href={`tel:${employee.phone}`} style={{ color: '#1976d2' }}>
                  {employee.phone}
                </a>
              ) : 'N/A'}
            </p>
            <p style={{ marginBottom: 0 }}>
              <strong>Ishga kirgan:</strong><br/>
              {employee.hire_date ? new Date(employee.hire_date).toLocaleDateString('uz-UZ') : 'N/A'}
            </p>
          </div>
        </div>

        {/* Qurilmalar */}
        <div style={{
          backgroundColor: '#f5f5f5',
          padding: 'clamp(15px, 3vw, 25px)',
          borderRadius: '10px',
          border: '3px solid #ff9800',
          gridColumn: 'span 1'
        }}>
          <h3 style={{
            color: '#e65100',
            marginBottom: '15px',
            fontSize: 'clamp(1.1rem, 3.5vw, 1.3rem)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            💻 Joriy Qurilmalar
          </h3>
          <div style={{
            textAlign: 'center',
            padding: '20px',
            fontSize: 'clamp(1.5rem, 4vw, 2rem)',
            fontWeight: 'bold',
            color: '#ff9800'
          }}>
            {employee.current_equipment_count || 0}
          </div>
          <p style={{
            textAlign: 'center',
            color: '#666',
            fontSize: 'clamp(0.9rem, 2.5vw, 1rem)'
          }}>
            Foydalanayotgan qurilmalar
          </p>
        </div>
      </div>

      {/* QR Kod */}
      {employee.qr_code && (
        <div style={{
          marginTop: '30px',
          padding: 'clamp(20px, 4vw, 30px)',
          backgroundColor: '#fff',
          borderRadius: '10px',
          border: '3px solid #9c27b0',
          textAlign: 'center'
        }}>
          <h3 style={{
            color: '#7b1fa2',
            marginBottom: '20px',
            fontSize: 'clamp(1.1rem, 3.5vw, 1.3rem)'
          }}>
            📱 QR Kod
          </h3>
          <img
            src={employee.qr_code}
            alt="QR Code"
            style={{
              maxWidth: '100%',
              width: 'clamp(200px, 40vw, 300px)',
              height: 'auto',
              border: '2px solid #e0e0e0',
              borderRadius: '8px'
            }}
          />
          <p style={{
            marginTop: '15px',
            color: '#666',
            fontSize: 'clamp(0.85rem, 2.5vw, 0.95rem)'
          }}>
            Telefon bilan skanerlang va ma'lumotlarni ko'ring
          </p>
        </div>
      )}
    </div>
  );
}

export default EmployeeDetail;

import React, { useState, useEffect } from 'react';
import { employeeAPI, equipmentAPI } from '../api';

function QRCodes() {
  const [employees, setEmployees] = useState([]);
  const [equipment, setEquipment] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('equipment');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [employeesRes, equipmentRes] = await Promise.all([
        employeeAPI.getAll(),
        equipmentAPI.getAll()
      ]);

      setEmployees(employeesRes.data.results || employeesRes.data);
      setEquipment(equipmentRes.data.results || equipmentRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Ma\'lumotlarni yuklashda xatolik:', error);
      setLoading(false);
    }
  };

  const downloadQRCode = (url, filename) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h1>QR Kodlar</h1>
        <p>Hodim va qurilma QR kodlarini ko'ring va yuklab oling</p>
      </div>

      <div className="action-buttons" style={{
        marginBottom: '20px',
        display: 'flex',
        flexWrap: 'wrap',
        gap: '10px',
        justifyContent: 'center'
      }}>
        <button
          className={`btn ${activeTab === 'equipment' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('equipment')}
          style={{
            flex: '1 1 auto',
            minWidth: '150px',
            maxWidth: '250px'
          }}
        >
          Qurilmalar QR Kodlari
        </button>
        <button
          className={`btn ${activeTab === 'employees' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('employees')}
          style={{
            flex: '1 1 auto',
            minWidth: '150px',
            maxWidth: '250px'
          }}
        >
          Hodimlar QR Kodlari
        </button>
      </div>

      {activeTab === 'equipment' && (
        <div className="data-table">
          <div className="table-header">
            <h2>Qurilmalar QR Kodlari</h2>
          </div>
          <div style={{
            padding: '15px',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(min(100%, 280px), 1fr))',
            gap: '20px'
          }}>
            {equipment.map((item) => (
              <div key={item.id} style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                borderRadius: '16px',
                padding: 'clamp(15px, 5vw, 25px)',
                textAlign: 'center',
                boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
                transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                position: 'relative',
                overflow: 'hidden'
              }}
              onTouchStart={(e) => {
                e.currentTarget.style.transform = 'scale(0.98)';
              }}
              onTouchEnd={(e) => {
                e.currentTarget.style.transform = 'scale(1)';
              }}
              onMouseEnter={(e) => {
                if (window.innerWidth > 768) {
                  e.currentTarget.style.transform = 'translateY(-5px)';
                  e.currentTarget.style.boxShadow = '0 15px 40px rgba(0,0,0,0.3)';
                }
              }}
              onMouseLeave={(e) => {
                if (window.innerWidth > 768) {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 10px 30px rgba(0,0,0,0.2)';
                }
              }}>
                <div style={{
                  position: 'absolute',
                  top: '-50px',
                  right: '-50px',
                  width: '150px',
                  height: '150px',
                  background: 'rgba(255,255,255,0.1)',
                  borderRadius: '50%'
                }}></div>

                <div style={{
                  background: 'rgba(255,255,255,0.15)',
                  borderRadius: '12px',
                  padding: '10px',
                  marginBottom: '15px',
                  backdropFilter: 'blur(10px)'
                }}>
                  <h3 style={{
                    margin: '0',
                    fontSize: 'clamp(16px, 4vw, 18px)',
                    color: 'white',
                    fontWeight: '600',
                    textShadow: '0 2px 4px rgba(0,0,0,0.2)',
                    wordBreak: 'break-word'
                  }}>{item.name}</h3>
                  <p style={{
                    color: '#f0f0f0',
                    margin: '8px 0 0 0',
                    fontSize: 'clamp(13px, 3.5vw, 14px)',
                    fontWeight: '500'
                  }}>
                    {item.inventory_number}
                  </p>
                </div>

                {item.qr_code ? (
                  <>
                    <div style={{
                      background: 'white',
                      borderRadius: '12px',
                      padding: '15px',
                      marginBottom: '15px',
                      boxShadow: '0 4px 15px rgba(0,0,0,0.1)'
                    }}>
                      <img
                        src={item.qr_code}
                        alt={`QR ${item.inventory_number}`}
                        style={{
                          width: '100%',
                          maxWidth: '200px',
                          height: 'auto',
                          aspectRatio: '1/1',
                          margin: '0 auto',
                          display: 'block'
                        }}
                      />
                    </div>

                    <div style={{ marginBottom: '10px' }}>
                      <button
                        className="btn btn-success"
                        onClick={() => downloadQRCode(item.qr_code, `${item.inventory_number}.png`)}
                        style={{
                          background: 'white',
                          color: '#667eea',
                          border: 'none',
                          padding: 'clamp(10px, 3vw, 12px) clamp(18px, 5vw, 24px)',
                          borderRadius: '8px',
                          fontWeight: '600',
                          fontSize: 'clamp(13px, 3.5vw, 14px)',
                          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                          transition: 'all 0.3s ease',
                          width: '100%',
                          maxWidth: '200px',
                          touchAction: 'manipulation'
                        }}
                        onMouseEnter={(e) => {
                          if (window.innerWidth > 768) {
                            e.currentTarget.style.background = '#f8f8f8';
                            e.currentTarget.style.transform = 'scale(1.05)';
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (window.innerWidth > 768) {
                            e.currentTarget.style.background = 'white';
                            e.currentTarget.style.transform = 'scale(1)';
                          }
                        }}
                      >
                        📥 Yuklab Olish
                      </button>
                    </div>

                    <p style={{
                      fontSize: '11px',
                      color: 'rgba(255,255,255,0.8)',
                      margin: '0',
                      fontFamily: 'monospace',
                      background: 'rgba(0,0,0,0.2)',
                      padding: '6px 12px',
                      borderRadius: '6px',
                      display: 'inline-block'
                    }}>
                      EQUIPMENT:{item.inventory_number}
                    </p>
                  </>
                ) : (
                  <p style={{ color: '#ffcccb', fontWeight: '500' }}>QR kod mavjud emas</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'employees' && (
        <div className="data-table">
          <div className="table-header">
            <h2>Hodimlar QR Kodlari</h2>
          </div>
          <div style={{
            padding: '15px',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(min(100%, 280px), 1fr))',
            gap: '20px'
          }}>
            {employees.map((employee) => (
              <div key={employee.id} style={{
                background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                borderRadius: '16px',
                padding: 'clamp(15px, 5vw, 25px)',
                textAlign: 'center',
                boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
                transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                position: 'relative',
                overflow: 'hidden'
              }}
              onTouchStart={(e) => {
                e.currentTarget.style.transform = 'scale(0.98)';
              }}
              onTouchEnd={(e) => {
                e.currentTarget.style.transform = 'scale(1)';
              }}
              onMouseEnter={(e) => {
                if (window.innerWidth > 768) {
                  e.currentTarget.style.transform = 'translateY(-5px)';
                  e.currentTarget.style.boxShadow = '0 15px 40px rgba(0,0,0,0.3)';
                }
              }}
              onMouseLeave={(e) => {
                if (window.innerWidth > 768) {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 10px 30px rgba(0,0,0,0.2)';
                }
              }}>
                <div style={{
                  position: 'absolute',
                  top: '-50px',
                  left: '-50px',
                  width: '150px',
                  height: '150px',
                  background: 'rgba(255,255,255,0.1)',
                  borderRadius: '50%'
                }}></div>

                <div style={{
                  width: '80px',
                  height: '80px',
                  borderRadius: '50%',
                  background: 'white',
                  margin: '0 auto 15px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '36px',
                  boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
                  position: 'relative',
                  zIndex: 1
                }}>
                  👤
                </div>

                <div style={{
                  background: 'rgba(255,255,255,0.15)',
                  borderRadius: '12px',
                  padding: '12px',
                  marginBottom: '15px',
                  backdropFilter: 'blur(10px)',
                  position: 'relative',
                  zIndex: 1
                }}>
                  <h3 style={{
                    margin: '0',
                    fontSize: 'clamp(16px, 4vw, 18px)',
                    color: 'white',
                    fontWeight: '600',
                    textShadow: '0 2px 4px rgba(0,0,0,0.2)',
                    wordBreak: 'break-word'
                  }}>{employee.full_name}</h3>
                  <p style={{
                    color: '#f0f0f0',
                    margin: '5px 0 0 0',
                    fontSize: 'clamp(12px, 3vw, 13px)',
                    fontWeight: '400'
                  }}>{employee.position}</p>
                  <p style={{
                    color: '#fff',
                    margin: '8px 0 0 0',
                    fontSize: 'clamp(13px, 3.5vw, 14px)',
                    fontWeight: '600'
                  }}>
                    {employee.employee_id}
                  </p>
                </div>

                {employee.qr_code ? (
                  <>
                    <div style={{
                      background: 'white',
                      borderRadius: '12px',
                      padding: '15px',
                      marginBottom: '15px',
                      boxShadow: '0 4px 15px rgba(0,0,0,0.1)',
                      position: 'relative',
                      zIndex: 1
                    }}>
                      <img
                        src={employee.qr_code}
                        alt={`QR ${employee.employee_id}`}
                        style={{
                          width: '200px',
                          height: '200px',
                          margin: '0 auto',
                          display: 'block'
                        }}
                      />
                    </div>

                    <div style={{ marginBottom: '10px', position: 'relative', zIndex: 1 }}>
                      <button
                        className="btn btn-success"
                        onClick={() => downloadQRCode(employee.qr_code, `${employee.employee_id}.png`)}
                        style={{
                          background: 'white',
                          color: '#f5576c',
                          border: 'none',
                          padding: 'clamp(10px, 3vw, 12px) clamp(18px, 5vw, 24px)',
                          borderRadius: '8px',
                          fontWeight: '600',
                          fontSize: 'clamp(13px, 3.5vw, 14px)',
                          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                          transition: 'all 0.3s ease',
                          width: '100%',
                          maxWidth: '200px',
                          touchAction: 'manipulation'
                        }}
                        onMouseEnter={(e) => {
                          if (window.innerWidth > 768) {
                            e.currentTarget.style.background = '#f8f8f8';
                            e.currentTarget.style.transform = 'scale(1.05)';
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (window.innerWidth > 768) {
                            e.currentTarget.style.background = 'white';
                            e.currentTarget.style.transform = 'scale(1)';
                          }
                        }}
                      >
                        📥 Yuklab Olish
                      </button>
                    </div>

                    <p style={{
                      fontSize: '11px',
                      color: 'rgba(255,255,255,0.8)',
                      margin: '0',
                      fontFamily: 'monospace',
                      background: 'rgba(0,0,0,0.2)',
                      padding: '6px 12px',
                      borderRadius: '6px',
                      display: 'inline-block',
                      position: 'relative',
                      zIndex: 1
                    }}>
                      EMPLOYEE:{employee.employee_id}
                    </p>
                  </>
                ) : (
                  <p style={{ color: '#ffcccb', fontWeight: '500' }}>QR kod mavjud emas</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default QRCodes;

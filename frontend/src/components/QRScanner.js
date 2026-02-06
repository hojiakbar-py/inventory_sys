import React, { useState } from 'react';
import { qrScanAPI } from '../api';

function QRScanner() {
  const [qrInput, setQrInput] = useState('');
  const [scanResult, setScanResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleScan = async () => {
    if (!qrInput.trim()) {
      setError('QR kod ma\'lumotini kiriting');
      return;
    }

    setLoading(true);
    setError(null);
    setScanResult(null);

    try {
      const response = await qrScanAPI.scan(qrInput);
      setScanResult(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Skaner xatolik:', error);
      setError(error.response?.data?.error || 'QR kodni skanerlashda xatolik');
      setLoading(false);
    }
  };

  const handleQuickScan = (qrData) => {
    setQrInput(qrData);
    qrScanAPI.scan(qrData)
      .then(response => {
        setScanResult(response.data);
        setError(null);
      })
      .catch(error => {
        setError(error.response?.data?.error || 'QR kodni skanerlashda xatolik');
      });
  };

  return (
    <div className="qr-scanner-container">
      <div className="page-header">
        <h1>🔍 QR Kod Skaner</h1>
        <p>Qurilma yoki hodim QR kodini skanerlang</p>
      </div>

      <div className="form-container" style={{ maxWidth: '800px', padding: 'clamp(15px, 3vw, 30px)' }}>
        <h2 style={{ fontSize: 'clamp(1.2rem, 4vw, 1.5rem)' }}>QR Kod Ma'lumotini Kiriting</h2>

        <div className="form-group">
          <label>QR Kod Ma'lumoti</label>
          <input
            type="text"
            value={qrInput}
            onChange={(e) => setQrInput(e.target.value)}
            placeholder="Masalan: EQUIPMENT:INV-001 yoki EMPLOYEE:EMP001"
            onKeyPress={(e) => e.key === 'Enter' && handleScan()}
          />
          <small style={{ display: 'block', marginTop: '5px', color: '#666' }}>
            QR kod formatini to'g'ri kiriting: EQUIPMENT:INV-XXX yoki EMPLOYEE:EMP-XXX
          </small>
        </div>

        <div className="form-actions">
          <button
            className="btn btn-primary"
            onClick={handleScan}
            disabled={loading}
          >
            {loading ? 'Skanerlanyapti...' : 'Skanerlash'}
          </button>
          <button
            className="btn btn-danger"
            onClick={() => {
              setQrInput('');
              setScanResult(null);
              setError(null);
            }}
          >
            Tozalash
          </button>
        </div>

        <div style={{ marginTop: '20px' }}>
          <p><strong>Tez skanerlash:</strong></p>
          <div className="action-buttons" style={{ marginTop: '10px' }}>
            <button className="btn btn-success" onClick={() => handleQuickScan('EQUIPMENT:INV-001')}>
              INV-001 (Noutbuk)
            </button>
            <button className="btn btn-success" onClick={() => handleQuickScan('EQUIPMENT:INV-002')}>
              INV-002 (Noutbuk)
            </button>
            <button className="btn btn-warning" onClick={() => handleQuickScan('EMPLOYEE:EMP001')}>
              EMP001 (Anvar)
            </button>
            <button className="btn btn-warning" onClick={() => handleQuickScan('EMPLOYEE:EMP002')}>
              EMP002 (Dilnoza)
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="alert alert-error" style={{ marginTop: '20px' }}>
          {error}
        </div>
      )}

      {scanResult && (
        <div className="form-container" style={{ marginTop: '30px', maxWidth: '1000px' }}>
          <h2>
            {scanResult.type === 'equipment' ? '🖥️ Qurilma Ma\'lumotlari' : '👤 Hodim Ma\'lumotlari'}
          </h2>

          {scanResult.type === 'equipment' && (
            <div>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: '20px',
                marginBottom: '20px'
              }}>
                <div style={{
                  backgroundColor: '#f5f5f5',
                  padding: '15px',
                  borderRadius: '8px',
                  border: '2px solid #e0e0e0'
                }}>
                  <h4 style={{ color: '#1976d2', marginBottom: '10px', fontSize: 'clamp(1rem, 3vw, 1.1rem)' }}>
                    📋 Asosiy Ma'lumotlar
                  </h4>
                  <p style={{ marginBottom: '8px', fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>
                    <strong>Nomi:</strong><br />{scanResult.data.name}
                  </p>
                  <p style={{ marginBottom: '8px', fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>
                    <strong>Inventar #:</strong><br />{scanResult.data.inventory_number}
                  </p>
                  <p style={{ marginBottom: '8px', fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>
                    <strong>Seriya #:</strong><br />{scanResult.data.serial_number || 'N/A'}
                  </p>
                  <p style={{ marginBottom: '8px', fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>
                    <strong>Kategoriya:</strong><br />{scanResult.data.category_name || 'N/A'}
                  </p>
                </div>
                <div style={{
                  backgroundColor: '#f5f5f5',
                  padding: '15px',
                  borderRadius: '8px',
                  border: '2px solid #e0e0e0'
                }}>
                  <h4 style={{ color: '#388e3c', marginBottom: '10px', fontSize: 'clamp(1rem, 3vw, 1.1rem)' }}>
                    🏭 Texnik Ma'lumotlar
                  </h4>
                  <p style={{ marginBottom: '8px', fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>
                    <strong>Ishlab chiqaruvchi:</strong><br />{scanResult.data.manufacturer || 'N/A'}
                  </p>
                  <p style={{ marginBottom: '8px', fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>
                    <strong>Model:</strong><br />{scanResult.data.model || 'N/A'}
                  </p>
                  <p style={{ marginBottom: '8px', fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>
                    <strong>Holati:</strong><br />
                    <span style={{
                      padding: '3px 8px',
                      borderRadius: '4px',
                      backgroundColor: '#4caf50',
                      color: 'white',
                      fontSize: 'clamp(0.8rem, 2vw, 0.9rem)'
                    }}>
                      {scanResult.data.status}
                    </span>
                  </p>
                  {scanResult.data.purchase_date && (
                    <p style={{ marginBottom: '8px', fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>
                      <strong>Xarid sanasi:</strong><br />{new Date(scanResult.data.purchase_date).toLocaleDateString('uz-UZ')}
                    </p>
                  )}
                  {scanResult.data.purchase_price && (
                    <p style={{ marginBottom: '8px', fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>
                      <strong>Xarid narxi:</strong><br />{Number(scanResult.data.purchase_price).toLocaleString('uz-UZ')} so'm
                    </p>
                  )}
                </div>
              </div>

              {scanResult.data.current_assignment && (
                <div style={{
                  backgroundColor: '#e8f5e9',
                  padding: 'clamp(12px, 3vw, 20px)',
                  borderRadius: '8px',
                  marginTop: '20px',
                  border: '2px solid #4caf50'
                }}>
                  <h3 style={{
                    color: '#2e7d32',
                    marginBottom: '15px',
                    fontSize: 'clamp(1.1rem, 3.5vw, 1.3rem)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}>
                    📍 Hozirgi Tayinlash
                  </h3>
                  <div style={{ fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>
                    <p style={{ marginBottom: '8px' }}><strong>Hodim:</strong> {scanResult.data.current_assignment.employee}</p>
                    <p style={{ marginBottom: '8px' }}><strong>Hodim ID:</strong> {scanResult.data.current_assignment.employee_id}</p>
                    <p style={{ marginBottom: '8px' }}><strong>Bo'lim:</strong> {scanResult.data.current_assignment.department || 'N/A'}</p>
                    <p style={{ marginBottom: '8px' }}><strong>Tayinlangan:</strong> {new Date(scanResult.data.current_assignment.assigned_date).toLocaleDateString('uz-UZ')}</p>
                    <p style={{ marginBottom: 0 }}>
                      <strong>Foydalanish muddati:</strong>{' '}
                      <span style={{
                        padding: '3px 10px',
                        borderRadius: '15px',
                        backgroundColor: '#4caf50',
                        color: 'white',
                        fontWeight: 'bold'
                      }}>
                        {scanResult.data.current_assignment.days_assigned} kun
                      </span>
                    </p>
                  </div>
                </div>
              )}

              {scanResult.data.last_inventory_check && (
                <div style={{ backgroundColor: '#fff3e0', padding: '15px', borderRadius: '5px', marginTop: '20px' }}>
                  <h3 style={{ color: '#e65100', marginBottom: '10px' }}>✅ Oxirgi Inventarizatsiya</h3>
                  <p><strong>Sana:</strong> {new Date(scanResult.data.last_inventory_check.check_date).toLocaleDateString('uz-UZ')}</p>
                  <p><strong>Tekshirgan:</strong> {scanResult.data.last_inventory_check.checked_by || 'N/A'}</p>
                  <p><strong>Holat:</strong> {scanResult.data.last_inventory_check.condition}</p>
                  <p><strong>Ishlayaptimi:</strong> {scanResult.data.last_inventory_check.is_functional ? 'Ha' : 'Yo\'q'}</p>
                </div>
              )}
            </div>
          )}

          {scanResult.type === 'employee' && (
            <div>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: '20px',
                marginBottom: '20px'
              }}>
                <div style={{
                  backgroundColor: '#f5f5f5',
                  padding: '15px',
                  borderRadius: '8px',
                  border: '2px solid #e0e0e0'
                }}>
                  <h4 style={{ color: '#1976d2', marginBottom: '10px', fontSize: 'clamp(1rem, 3vw, 1.1rem)' }}>
                    👤 Shaxsiy Ma'lumotlar
                  </h4>
                  <p style={{ marginBottom: '8px', fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>
                    <strong>F.I.O:</strong><br />{scanResult.data.full_name}
                  </p>
                  <p style={{ marginBottom: '8px', fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>
                    <strong>Hodim ID:</strong><br />{scanResult.data.employee_id}
                  </p>
                  <p style={{ marginBottom: '8px', fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>
                    <strong>Lavozim:</strong><br />{scanResult.data.position}
                  </p>
                  <p style={{ marginBottom: 0, fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>
                    <strong>Bo'lim:</strong><br />{scanResult.data.department_name || 'N/A'}
                  </p>
                </div>
                <div style={{
                  backgroundColor: '#f5f5f5',
                  padding: '15px',
                  borderRadius: '8px',
                  border: '2px solid #e0e0e0'
                }}>
                  <h4 style={{ color: '#388e3c', marginBottom: '10px', fontSize: 'clamp(1rem, 3vw, 1.1rem)' }}>
                    📞 Aloqa Ma'lumotlari
                  </h4>
                  <p style={{ marginBottom: '8px', fontSize: 'clamp(0.9rem, 2.5vw, 1rem)', wordBreak: 'break-all' }}>
                    <strong>Email:</strong><br />{scanResult.data.email || 'N/A'}
                  </p>
                  <p style={{ marginBottom: '8px', fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>
                    <strong>Telefon:</strong><br />{scanResult.data.phone || 'N/A'}
                  </p>
                  <p style={{ marginBottom: 0, fontSize: 'clamp(0.9rem, 2.5vw, 1rem)' }}>
                    <strong>Ishga kirgan:</strong><br />{new Date(scanResult.data.hire_date).toLocaleDateString('uz-UZ')}
                  </p>
                </div>
              </div>

              {scanResult.current_equipment && scanResult.current_equipment.length > 0 && (
                <div style={{
                  backgroundColor: '#e3f2fd',
                  padding: 'clamp(12px, 3vw, 20px)',
                  borderRadius: '8px',
                  marginTop: '20px',
                  border: '2px solid #2196f3'
                }}>
                  <h3 style={{
                    color: '#1565c0',
                    marginBottom: '15px',
                    fontSize: 'clamp(1.1rem, 3.5vw, 1.3rem)'
                  }}>
                    💻 Joriy Qurilmalar ({scanResult.current_equipment.length})
                  </h3>
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', minWidth: '500px', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr style={{ backgroundColor: '#bbdefb' }}>
                          <th style={{
                            padding: 'clamp(8px, 2vw, 12px)',
                            textAlign: 'left',
                            fontSize: 'clamp(0.85rem, 2.5vw, 0.95rem)',
                            fontWeight: 'bold'
                          }}>
                            Inventar #
                          </th>
                          <th style={{
                            padding: 'clamp(8px, 2vw, 12px)',
                            textAlign: 'left',
                            fontSize: 'clamp(0.85rem, 2.5vw, 0.95rem)',
                            fontWeight: 'bold'
                          }}>
                            Nomi
                          </th>
                          <th style={{
                            padding: 'clamp(8px, 2vw, 12px)',
                            textAlign: 'left',
                            fontSize: 'clamp(0.85rem, 2.5vw, 0.95rem)',
                            fontWeight: 'bold'
                          }}>
                            Tayinlangan
                          </th>
                          <th style={{
                            padding: 'clamp(8px, 2vw, 12px)',
                            textAlign: 'left',
                            fontSize: 'clamp(0.85rem, 2.5vw, 0.95rem)',
                            fontWeight: 'bold'
                          }}>
                            Muddat
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {scanResult.current_equipment.map((eq, index) => (
                          <tr key={index} style={{ borderBottom: '1px solid #90caf9' }}>
                            <td style={{
                              padding: 'clamp(8px, 2vw, 12px)',
                              fontSize: 'clamp(0.85rem, 2.5vw, 0.95rem)'
                            }}>
                              {eq.inventory_number}
                            </td>
                            <td style={{
                              padding: 'clamp(8px, 2vw, 12px)',
                              fontSize: 'clamp(0.85rem, 2.5vw, 0.95rem)'
                            }}>
                              {eq.name}
                            </td>
                            <td style={{
                              padding: 'clamp(8px, 2vw, 12px)',
                              fontSize: 'clamp(0.85rem, 2.5vw, 0.95rem)'
                            }}>
                              {new Date(eq.assigned_date).toLocaleDateString('uz-UZ')}
                            </td>
                            <td style={{
                              padding: 'clamp(8px, 2vw, 12px)',
                              fontSize: 'clamp(0.85rem, 2.5vw, 0.95rem)'
                            }}>
                              <span style={{
                                padding: '3px 8px',
                                borderRadius: '12px',
                                backgroundColor: '#2196f3',
                                color: 'white',
                                fontWeight: 'bold',
                                fontSize: 'clamp(0.75rem, 2vw, 0.85rem)'
                              }}>
                                {eq.days_assigned} kun
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default QRScanner;

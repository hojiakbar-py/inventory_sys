import React, { useState } from 'react';
import { assignmentAPI, inventoryCheckAPI, maintenanceAPI } from '../api';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import '../App.css';

function History() {
  const [selectedDate, setSelectedDate] = useState('');
  const [historyData, setHistoryData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Date range filters
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [assignments, setAssignments] = useState([]);
  const [inventoryChecks, setInventoryChecks] = useState([]);
  const [maintenanceRecords, setMaintenanceRecords] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);

  const handleDateSearch = async () => {
    if (!selectedDate) {
      setError('Iltimos, sanani tanlang');
      return;
    }

    setLoading(true);
    setError('');
    setHistoryData(null);

    try {
      // Fetch all data UP TO the selected date (inclusive)
      const [assignmentsRes, checksRes, maintenanceRes] = await Promise.all([
        assignmentAPI.getAll({ date_to: selectedDate }),
        inventoryCheckAPI.getAll({ date_to: selectedDate }),
        maintenanceAPI.getAll({ date_to: selectedDate })
      ]);

      // Combine all data
      setHistoryData({
        date: selectedDate,
        assignments: assignmentsRes.data.results || assignmentsRes.data,
        inventoryChecks: checksRes.data.results || checksRes.data,
        maintenanceRecords: maintenanceRes.data.results || maintenanceRes.data,
        total_assigned_equipment: (assignmentsRes.data.results || assignmentsRes.data).length,
        inventory_checks_count: (checksRes.data.results || checksRes.data).length,
        maintenance_records_count: (maintenanceRes.data.results || maintenanceRes.data).length
      });
    } catch (err) {
      console.error('Sana bo\'yicha qidirishda xatolik:', err);
      setError(err.response?.data?.error || 'Ma\'lumotlarni yuklashda xatolik yuz berdi');
    } finally {
      setLoading(false);
    }
  };

  const handleExportSpecificDate = () => {
    if (!selectedDate) {
      setError('Iltimos, avval sanani tanlang va qidirish tugmasini bosing');
      return;
    }

    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    window.open(
      `${API_BASE_URL}/assignments/export_csv/?date_to=${selectedDate}`,
      '_blank'
    );
  };

  const handleExportSpecificDateChecks = () => {
    if (!selectedDate) {
      setError('Iltimos, avval sanani tanlang va qidirish tugmasini bosing');
      return;
    }

    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    window.open(
      `${API_BASE_URL}/inventory-checks/export_csv/?date_to=${selectedDate}`,
      '_blank'
    );
  };

  const handleExportSpecificDateMaintenance = () => {
    if (!selectedDate) {
      setError('Iltimos, avval sanani tanlang va qidirish tugmasini bosing');
      return;
    }

    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    window.open(
      `${API_BASE_URL}/maintenance-records/export_csv/?date_to=${selectedDate}`,
      '_blank'
    );
  };

  const handleDateRangeSearch = async () => {
    if (!dateFrom || !dateTo) {
      setError('Iltimos, boshlanish va tugash sanalarini tanlang');
      return;
    }

    if (new Date(dateFrom) > new Date(dateTo)) {
      setError('Boshlanish sanasi tugash sanasidan kichik bo\'lishi kerak');
      return;
    }

    setLoading(true);
    setError('');
    setAssignments([]);
    setInventoryChecks([]);
    setMaintenanceRecords([]);
    setAuditLogs([]);

    try {
      const [assignmentsRes, checksRes, maintenanceRes] = await Promise.all([
        assignmentAPI.getAll({ date_from: dateFrom, date_to: dateTo }),
        inventoryCheckAPI.getAll({ date_from: dateFrom, date_to: dateTo }),
        maintenanceAPI.getAll({ date_from: dateFrom, date_to: dateTo })
      ]);

      setAssignments(assignmentsRes.data.results || assignmentsRes.data);
      setInventoryChecks(checksRes.data.results || checksRes.data);
      setMaintenanceRecords(maintenanceRes.data.results || maintenanceRes.data);
      setAuditLogs([]);
    } catch (err) {
      console.error('Sana oralig\'i bo\'yicha qidirishda xatolik:', err);
      setError(err.response?.data?.error || 'Ma\'lumotlarni yuklashda xatolik yuz berdi');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('uz-UZ', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('uz-UZ', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleExportDateRange = () => {
    if (!dateFrom || !dateTo) {
      setError('Iltimos, sana oralig\'ini tanlang');
      return;
    }

    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    window.open(
      `${API_BASE_URL}/assignments/export_csv/?date_from=${dateFrom}&date_to=${dateTo}`,
      '_blank'
    );
  };

  const handleExportInventoryChecks = () => {
    if (!dateFrom || !dateTo) {
      setError('Iltimos, sana oralig\'ini tanlang');
      return;
    }

    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    window.open(
      `${API_BASE_URL}/inventory-checks/export_csv/?date_from=${dateFrom}&date_to=${dateTo}`,
      '_blank'
    );
  };

  const handleExportMaintenance = () => {
    if (!dateFrom || !dateTo) {
      setError('Iltimos, sana oralig\'ini tanlang');
      return;
    }

    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    window.open(
      `${API_BASE_URL}/maintenance-records/export_csv/?date_from=${dateFrom}&date_to=${dateTo}`,
      '_blank'
    );
  };

  return (
    <div className="history-container">
      {/* Modern Header */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '40px',
        borderRadius: '16px',
        marginBottom: '30px',
        color: 'white',
        boxShadow: '0 10px 30px rgba(102, 126, 234, 0.3)'
      }}>
        <h1 style={{ margin: 0, fontSize: '32px', fontWeight: 'bold', marginBottom: '10px' }}>
          📅 Tarixiy Ma'lumotlar
        </h1>
        <p style={{ margin: 0, opacity: 0.95, fontSize: '16px' }}>
          Qurilmalar va hodimlar faoliyati tarixi
        </p>
      </div>

      {/* Specific Date Search - Modern Card */}
      <div className="form-container" style={{
        marginBottom: '30px',
        background: 'white',
        borderRadius: '16px',
        padding: '30px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
        border: '1px solid #f0f0f0'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          marginBottom: '12px'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '20px'
          }}>
            📆
          </div>
          <h2 style={{ margin: 0, fontSize: '24px', color: '#2d3748' }}>
            Muayyan sanada ma'lumotlar
          </h2>
        </div>
        <p style={{ color: '#718096', marginBottom: '24px', marginLeft: '52px' }}>
          Tanlangan sanagacha bo'lgan barcha tayinlash, tekshiruv va ta'mirlash ma'lumotlari
        </p>

        <div className="history-date-search">
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="form-control"
            style={{
              flex: 1,
              padding: '12px 16px',
              fontSize: '16px',
              border: '2px solid #e2e8f0',
              borderRadius: '10px',
              transition: 'all 0.3s ease'
            }}
            onFocus={(e) => e.target.style.borderColor = '#667eea'}
            onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
          />
          <button
            onClick={handleDateSearch}
            disabled={loading}
            className="btn btn-primary"
            style={{
              minWidth: '140px',
              padding: '12px 24px',
              fontSize: '15px',
              fontWeight: '600',
              borderRadius: '10px',
              background: loading ? '#cbd5e0' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              border: 'none',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: loading ? 'none' : '0 4px 12px rgba(102, 126, 234, 0.4)'
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.5)';
              }
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
            }}
          >
            {loading ? '⏳ Yuklanmoqda...' : '🔍 Qidirish'}
          </button>
        </div>

        {error && (
          <ErrorMessage
            error={{ response: { data: { error: error } } }}
            onRetry={() => {
              setError('');
              if (selectedDate) handleDateSearch();
            }}
          />
        )}

        {historyData && (
          <div style={{ marginTop: '30px' }}>
            <div style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              padding: '25px',
              borderRadius: '12px',
              color: 'white',
              marginBottom: '25px'
            }}>
              <h3 style={{ margin: '0 0 15px 0' }}>
                {formatDate(historyData.date)} sanasigacha bo'lgan barcha ma'lumotlar
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                <div>
                  <div style={{ fontSize: '32px', fontWeight: 'bold' }}>{historyData.total_assigned_equipment}</div>
                  <div style={{ opacity: 0.9 }}>Tayinlashlar</div>
                </div>
                <div>
                  <div style={{ fontSize: '32px', fontWeight: 'bold' }}>{historyData.inventory_checks_count}</div>
                  <div style={{ opacity: 0.9 }}>Tekshiruvlar</div>
                </div>
                <div>
                  <div style={{ fontSize: '32px', fontWeight: 'bold' }}>{historyData.maintenance_records_count}</div>
                  <div style={{ opacity: 0.9 }}>Ta'mirlashlar</div>
                </div>
              </div>
            </div>

            {/* Export buttons for specific date */}
            <div style={{
              marginBottom: '24px',
              padding: '20px',
              background: 'linear-gradient(135deg, #f6f8fb 0%, #e9ecef 100%)',
              borderRadius: '12px',
              border: '2px dashed #cbd5e0'
            }}>
              <div style={{
                marginBottom: '16px',
                fontWeight: '600',
                color: '#2d3748',
                fontSize: '15px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <span style={{ fontSize: '20px' }}>📥</span>
                Natijalarni CSV formatda yuklab olish
              </div>
              <div className="action-buttons">
                <button
                  onClick={handleExportSpecificDate}
                  className="btn"
                  style={{
                    padding: '10px 20px',
                    fontSize: '14px',
                    fontWeight: '600',
                    borderRadius: '8px',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    border: 'none',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    boxShadow: '0 2px 8px rgba(102, 126, 234, 0.3)'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = '0 2px 8px rgba(102, 126, 234, 0.3)';
                  }}
                >
                  📋 Tayinlashlar CSV
                </button>
                <button
                  onClick={handleExportSpecificDateChecks}
                  className="btn"
                  style={{
                    padding: '10px 20px',
                    fontSize: '14px',
                    fontWeight: '600',
                    borderRadius: '8px',
                    background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                    color: 'white',
                    border: 'none',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    boxShadow: '0 2px 8px rgba(240, 147, 251, 0.3)'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 4px 12px rgba(240, 147, 251, 0.4)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = '0 2px 8px rgba(240, 147, 251, 0.3)';
                  }}
                >
                  ✅ Tekshiruvlar CSV
                </button>
                <button
                  onClick={handleExportSpecificDateMaintenance}
                  className="btn"
                  style={{
                    padding: '10px 20px',
                    fontSize: '14px',
                    fontWeight: '600',
                    borderRadius: '8px',
                    background: 'linear-gradient(135deg, #FA8BFF 0%, #2BD2FF 90%)',
                    color: 'white',
                    border: 'none',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    boxShadow: '0 2px 8px rgba(43, 210, 255, 0.3)'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 4px 12px rgba(43, 210, 255, 0.4)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = '0 2px 8px rgba(43, 210, 255, 0.3)';
                  }}
                >
                  🔧 Ta'mirlashlar CSV
                </button>
              </div>
            </div>

            {/* Assignments */}
            {historyData.assignments && historyData.assignments.length > 0 && (
              <div style={{ marginBottom: '30px' }}>
                <h3 style={{
                  padding: '15px',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  borderRadius: '8px',
                  marginBottom: '15px'
                }}>
                  📋 Tayinlashlar ({historyData.assignments.length})
                </h3>
                <div style={{ display: 'grid', gap: '10px' }}>
                  {historyData.assignments.map((assignment) => (
                    <div key={assignment.id} className="form-container" style={{
                      padding: '15px',
                      borderLeft: '4px solid #667eea'
                    }}>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                        <div>
                          <strong style={{ color: '#667eea' }}>Qurilma:</strong>{' '}
                          {assignment.equipment_name || 'N/A'}
                        </div>
                        <div>
                          <strong style={{ color: '#667eea' }}>Hodim:</strong>{' '}
                          {assignment.employee_name || 'N/A'}
                        </div>
                        <div>
                          <strong style={{ color: '#999' }}>Tayinlangan:</strong>{' '}
                          {formatDate(assignment.assigned_date)}
                        </div>
                        {assignment.return_date && (
                          <div>
                            <strong style={{ color: '#999' }}>Qaytarilgan:</strong>{' '}
                            {formatDate(assignment.return_date)}
                          </div>
                        )}
                        {assignment.is_returned === false && (
                          <div style={{ color: '#28a745', fontWeight: 'bold' }}>
                            ✓ Faol
                          </div>
                        )}
                      </div>
                      {assignment.notes && (
                        <div style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
                          <strong>Izoh:</strong> {assignment.notes}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Inventory Checks */}
            {historyData.inventoryChecks && historyData.inventoryChecks.length > 0 && (
              <div style={{ marginBottom: '30px' }}>
                <h3 style={{
                  padding: '15px',
                  background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                  color: 'white',
                  borderRadius: '8px',
                  marginBottom: '15px'
                }}>
                  ✅ Inventarizatsiya tekshiruvlari ({historyData.inventoryChecks.length})
                </h3>
                <div style={{ display: 'grid', gap: '10px' }}>
                  {historyData.inventoryChecks.map((check) => (
                    <div key={check.id} className="form-container" style={{
                      padding: '15px',
                      borderLeft: '4px solid #f093fb'
                    }}>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                        <div>
                          <strong style={{ color: '#f093fb' }}>Qurilma:</strong>{' '}
                          {check.equipment_name || 'N/A'}
                        </div>
                        <div>
                          <strong style={{ color: '#f093fb' }}>Joylashuv:</strong>{' '}
                          {check.location || 'N/A'}
                        </div>
                        <div>
                          <strong style={{ color: '#999' }}>Tekshirilgan:</strong>{' '}
                          {formatDateTime(check.check_date)}
                        </div>
                        <div>
                          <strong style={{ color: '#999' }}>Ishlayaptimi:</strong>{' '}
                          {check.is_functional ? '✓ Ha' : '✗ Yo\'q'}
                        </div>
                      </div>
                      <div style={{ marginTop: '10px' }}>
                        <strong>Holat:</strong> {check.condition}
                      </div>
                      {check.notes && (
                        <div style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
                          <strong>Izoh:</strong> {check.notes}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Maintenance Records */}
            {historyData.maintenanceRecords && historyData.maintenanceRecords.length > 0 && (
              <div style={{ marginBottom: '30px' }}>
                <h3 style={{
                  padding: '15px',
                  background: 'linear-gradient(135deg, #FA8BFF 0%, #2BD2FF 90%)',
                  color: 'white',
                  borderRadius: '8px',
                  marginBottom: '15px'
                }}>
                  🔧 Ta'mirlash yozuvlari ({historyData.maintenanceRecords.length})
                </h3>
                <div style={{ display: 'grid', gap: '10px' }}>
                  {historyData.maintenanceRecords.map((record) => (
                    <div key={record.id} className="form-container" style={{
                      padding: '15px',
                      borderLeft: '4px solid #2BD2FF'
                    }}>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                        <div>
                          <strong style={{ color: '#2BD2FF' }}>Qurilma:</strong>{' '}
                          {record.equipment_name || 'N/A'}
                        </div>
                        <div>
                          <strong style={{ color: '#2BD2FF' }}>Turi:</strong>{' '}
                          {record.maintenance_type || 'N/A'}
                        </div>
                        <div>
                          <strong style={{ color: '#999' }}>Bajargan:</strong>{' '}
                          {record.performed_by || 'N/A'}
                        </div>
                        <div>
                          <strong style={{ color: '#999' }}>Sana:</strong>{' '}
                          {record.performed_date ? formatDate(record.performed_date) : 'Rejalashtirilingan'}
                        </div>
                        {record.cost && (
                          <div>
                            <strong style={{ color: '#999' }}>Xarajat:</strong>{' '}
                            {record.cost} so'm
                          </div>
                        )}
                      </div>
                      <div style={{ marginTop: '10px' }}>
                        <strong>Tavsif:</strong> {record.description}
                      </div>
                      {record.notes && (
                        <div style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
                          <strong>Izoh:</strong> {record.notes}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* No data message */}
            {(!historyData.assignments || historyData.assignments.length === 0) &&
             (!historyData.inventoryChecks || historyData.inventoryChecks.length === 0) &&
             (!historyData.maintenanceRecords || historyData.maintenanceRecords.length === 0) && (
              <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                Bu sanada hech qanday ma'lumot topilmadi
              </div>
            )}
          </div>
        )}
      </div>

      {/* Date Range Search - Modern Card */}
      <div className="form-container" style={{
        background: 'white',
        borderRadius: '16px',
        padding: '30px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
        border: '1px solid #f0f0f0'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          marginBottom: '12px'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '20px'
          }}>
            📊
          </div>
          <h2 style={{ margin: 0, fontSize: '24px', color: '#2d3748' }}>
            Sana oralig'idagi ma'lumotlar
          </h2>
        </div>
        <p style={{ color: '#718096', marginBottom: '24px', marginLeft: '52px' }}>
          Muayyan davrdagi barcha harakatlar va ma'lumotlar
        </p>

        <div className="history-date-range-search">
          <div className="form-group" style={{ margin: 0 }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              color: '#4a5568',
              fontSize: '14px',
              fontWeight: '600'
            }}>
              Boshlanish sanasi
            </label>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="form-control"
              style={{
                padding: '12px 16px',
                fontSize: '16px',
                border: '2px solid #e2e8f0',
                borderRadius: '10px',
                transition: 'all 0.3s ease',
                width: '100%'
              }}
              onFocus={(e) => e.target.style.borderColor = '#48bb78'}
              onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
            />
          </div>
          <div className="form-group" style={{ margin: 0 }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              color: '#4a5568',
              fontSize: '14px',
              fontWeight: '600'
            }}>
              Tugash sanasi
            </label>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="form-control"
              style={{
                padding: '12px 16px',
                fontSize: '16px',
                border: '2px solid #e2e8f0',
                borderRadius: '10px',
                transition: 'all 0.3s ease',
                width: '100%'
              }}
              onFocus={(e) => e.target.style.borderColor = '#48bb78'}
              onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
            />
          </div>
          <button
            onClick={handleDateRangeSearch}
            disabled={loading}
            className="btn btn-success"
            style={{
              minWidth: '140px',
              padding: '12px 24px',
              fontSize: '15px',
              fontWeight: '600',
              borderRadius: '10px',
              background: loading ? '#cbd5e0' : 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)',
              border: 'none',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: loading ? 'none' : '0 4px 12px rgba(72, 187, 120, 0.4)',
              color: 'white'
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 6px 20px rgba(72, 187, 120, 0.5)';
              }
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 4px 12px rgba(72, 187, 120, 0.4)';
            }}
          >
            {loading ? '⏳ Yuklanmoqda...' : '🔍 Qidirish'}
          </button>
        </div>

        {/* Export buttons - Modern Style */}
        {(dateFrom && dateTo) && (
          <div style={{
            marginTop: '24px',
            padding: '20px',
            background: 'linear-gradient(135deg, #f6f8fb 0%, #e9ecef 100%)',
            borderRadius: '12px',
            border: '2px dashed #cbd5e0'
          }}>
            <div style={{
              marginBottom: '16px',
              fontWeight: '600',
              color: '#2d3748',
              fontSize: '15px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <span style={{ fontSize: '20px' }}>📥</span>
              Natijalarni eksport qilish
            </div>
            <div className="action-buttons">
              <button
                onClick={handleExportDateRange}
                className="btn"
                style={{
                  padding: '10px 20px',
                  fontSize: '14px',
                  fontWeight: '600',
                  borderRadius: '8px',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  border: 'none',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  boxShadow: '0 2px 8px rgba(102, 126, 234, 0.3)'
                }}
                onMouseEnter={(e) => {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 2px 8px rgba(102, 126, 234, 0.3)';
                }}
              >
                📋 Tayinlashlar CSV
              </button>
              <button
                onClick={handleExportInventoryChecks}
                className="btn"
                style={{
                  padding: '10px 20px',
                  fontSize: '14px',
                  fontWeight: '600',
                  borderRadius: '8px',
                  background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                  color: 'white',
                  border: 'none',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  boxShadow: '0 2px 8px rgba(240, 147, 251, 0.3)'
                }}
                onMouseEnter={(e) => {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 4px 12px rgba(240, 147, 251, 0.4)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 2px 8px rgba(240, 147, 251, 0.3)';
                }}
              >
                ✅ Tekshiruvlar CSV
              </button>
              <button
                onClick={handleExportMaintenance}
                className="btn"
                style={{
                  padding: '10px 20px',
                  fontSize: '14px',
                  fontWeight: '600',
                  borderRadius: '8px',
                  background: 'linear-gradient(135deg, #FA8BFF 0%, #2BD2FF 90%)',
                  color: 'white',
                  border: 'none',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  boxShadow: '0 2px 8px rgba(43, 210, 255, 0.3)'
                }}
                onMouseEnter={(e) => {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 4px 12px rgba(43, 210, 255, 0.4)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 2px 8px rgba(43, 210, 255, 0.3)';
                }}
              >
                🔧 Ta'mirlashlar CSV
              </button>
            </div>
          </div>
        )}

        {loading && (
          <LoadingSpinner size="large" text="Ma'lumotlar yuklanmoqda..." />
        )}

        {!loading && dateFrom && dateTo &&
         assignments.length === 0 &&
         inventoryChecks.length === 0 &&
         maintenanceRecords.length === 0 &&
         auditLogs.length === 0 && (
          <div style={{
            textAlign: 'center',
            padding: '60px 40px',
            background: 'linear-gradient(135deg, #f6f8fb 0%, #e9ecef 100%)',
            borderRadius: '16px',
            marginTop: '24px'
          }}>
            <div style={{ fontSize: '64px', marginBottom: '16px', opacity: 0.6 }}>
              📭
            </div>
            <h3 style={{ color: '#2d3748', marginBottom: '8px', fontSize: '20px' }}>
              Ma'lumot topilmadi
            </h3>
            <p style={{ color: '#718096', margin: 0 }}>
              Tanlangan sana oralig'ida hech qanday ma'lumot yo'q
            </p>
          </div>
        )}

        {(assignments.length > 0 || inventoryChecks.length > 0 || maintenanceRecords.length > 0 || auditLogs.length > 0) && (
          <div style={{ marginTop: '24px' }}>
            {/* Assignments */}
            {assignments.length > 0 && (
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{
                  padding: '16px 20px',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  borderRadius: '12px',
                  marginBottom: '16px',
                  fontSize: '18px',
                  fontWeight: '600',
                  boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px'
                }}>
                  <span>📋</span>
                  <span>Tayinlashlar</span>
                  <span style={{
                    marginLeft: 'auto',
                    background: 'rgba(255, 255, 255, 0.25)',
                    padding: '4px 12px',
                    borderRadius: '20px',
                    fontSize: '14px',
                    fontWeight: 'bold'
                  }}>
                    {assignments.length}
                  </span>
                </h3>
                <div style={{ display: 'grid', gap: '12px' }}>
                  {assignments.map((assignment) => (
                    <div key={assignment.id} style={{
                      padding: '20px',
                      background: 'white',
                      borderRadius: '12px',
                      borderLeft: '4px solid #667eea',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.boxShadow = '0 4px 16px rgba(102, 126, 234, 0.2)';
                      e.currentTarget.style.transform = 'translateY(-2px)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
                      e.currentTarget.style.transform = 'translateY(0)';
                    }}>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                        <div>
                          <strong style={{ color: '#667eea' }}>Qurilma:</strong>{' '}
                          {assignment.equipment_name || 'N/A'}
                        </div>
                        <div>
                          <strong style={{ color: '#667eea' }}>Hodim:</strong>{' '}
                          {assignment.employee_name || 'N/A'}
                        </div>
                        <div>
                          <strong style={{ color: '#999' }}>Tayinlangan:</strong>{' '}
                          {formatDate(assignment.assigned_date)}
                        </div>
                        {assignment.return_date && (
                          <div>
                            <strong style={{ color: '#999' }}>Qaytarilgan:</strong>{' '}
                            {formatDate(assignment.return_date)}
                          </div>
                        )}
                        {assignment.is_returned === false && (
                          <div style={{ color: '#28a745', fontWeight: 'bold' }}>
                            ✓ Faol
                          </div>
                        )}
                      </div>
                      {assignment.notes && (
                        <div style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
                          <strong>Izoh:</strong> {assignment.notes}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Inventory Checks */}
            {inventoryChecks.length > 0 && (
              <div style={{ marginBottom: '30px' }}>
                <h3 style={{
                  padding: '15px',
                  background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                  color: 'white',
                  borderRadius: '8px',
                  marginBottom: '15px'
                }}>
                  ✅ Inventarizatsiya tekshiruvlari ({inventoryChecks.length})
                </h3>
                <div style={{ display: 'grid', gap: '10px' }}>
                  {inventoryChecks.map((check) => (
                    <div key={check.id} className="form-container" style={{
                      padding: '15px',
                      borderLeft: '4px solid #f093fb'
                    }}>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                        <div>
                          <strong style={{ color: '#f093fb' }}>Qurilma:</strong>{' '}
                          {check.equipment_name || 'N/A'}
                        </div>
                        <div>
                          <strong style={{ color: '#f093fb' }}>Joylashuv:</strong>{' '}
                          {check.location || 'N/A'}
                        </div>
                        <div>
                          <strong style={{ color: '#999' }}>Tekshirilgan:</strong>{' '}
                          {formatDateTime(check.check_date)}
                        </div>
                        <div>
                          <strong style={{ color: '#999' }}>Ishlayaptimi:</strong>{' '}
                          {check.is_functional ? '✓ Ha' : '✗ Yo\'q'}
                        </div>
                      </div>
                      <div style={{ marginTop: '10px' }}>
                        <strong>Holat:</strong> {check.condition}
                      </div>
                      {check.notes && (
                        <div style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
                          <strong>Izoh:</strong> {check.notes}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Maintenance Records */}
            {maintenanceRecords.length > 0 && (
              <div style={{ marginBottom: '30px' }}>
                <h3 style={{
                  padding: '15px',
                  background: 'linear-gradient(135deg, #FA8BFF 0%, #2BD2FF 90%)',
                  color: 'white',
                  borderRadius: '8px',
                  marginBottom: '15px'
                }}>
                  🔧 Ta'mirlash yozuvlari ({maintenanceRecords.length})
                </h3>
                <div style={{ display: 'grid', gap: '10px' }}>
                  {maintenanceRecords.map((record) => (
                    <div key={record.id} className="form-container" style={{
                      padding: '15px',
                      borderLeft: '4px solid #2BD2FF'
                    }}>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                        <div>
                          <strong style={{ color: '#2BD2FF' }}>Qurilma:</strong>{' '}
                          {record.equipment_name || 'N/A'}
                        </div>
                        <div>
                          <strong style={{ color: '#2BD2FF' }}>Turi:</strong>{' '}
                          {record.maintenance_type || 'N/A'}
                        </div>
                        <div>
                          <strong style={{ color: '#999' }}>Bajargan:</strong>{' '}
                          {record.performed_by || 'N/A'}
                        </div>
                        <div>
                          <strong style={{ color: '#999' }}>Sana:</strong>{' '}
                          {record.performed_date ? formatDate(record.performed_date) : 'Rejalashtirilingan'}
                        </div>
                        {record.cost && (
                          <div>
                            <strong style={{ color: '#999' }}>Xarajat:</strong>{' '}
                            {record.cost} so'm
                          </div>
                        )}
                      </div>
                      <div style={{ marginTop: '10px' }}>
                        <strong>Tavsif:</strong> {record.description}
                      </div>
                      {record.notes && (
                        <div style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
                          <strong>Izoh:</strong> {record.notes}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Audit Logs */}
            {auditLogs.length > 0 && (
              <div>
                <h3 style={{
                  padding: '15px',
                  background: 'linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%)',
                  color: 'white',
                  borderRadius: '8px',
                  marginBottom: '15px'
                }}>
                  📝 Harakatlar tarixi ({auditLogs.length})
                </h3>
                <div style={{ display: 'grid', gap: '10px' }}>
                  {auditLogs.map((log) => (
                    <div key={log.id} className="card" style={{ padding: '15px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <strong>{log.user_name || 'Tizim'}</strong> - {log.action_display}
                          {log.model_name && ` (${log.model_name})`}
                          {log.object_repr && `: ${log.object_repr}`}
                        </div>
                        <div style={{ color: '#999', fontSize: '14px' }}>
                          {formatDateTime(log.timestamp)}
                        </div>
                      </div>
                      {log.description && (
                        <div style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
                          {log.description}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default History;

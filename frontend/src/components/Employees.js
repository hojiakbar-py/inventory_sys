import React, { useState, useEffect, useRef } from 'react';
import { employeeAPI, departmentAPI } from '../api';
import axios from 'axios';

function Employees() {
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('');
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    loadData();
  }, [searchTerm, selectedDepartment]);

  const loadData = async () => {
    try {
      const params = {};
      if (searchTerm) params.search = searchTerm;
      if (selectedDepartment) params.department = selectedDepartment;

      const [employeesRes, departmentsRes] = await Promise.all([
        employeeAPI.getAll(params),
        departmentAPI.getAll()
      ]);

      setEmployees(employeesRes.data.results || employeesRes.data);
      setDepartments(departmentsRes.data.results || departmentsRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Ma\'lumotlarni yuklashda xatolik:', error);
      setLoading(false);
    }
  };

  const handleExportCSV = () => {
    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    window.open(`${API_BASE_URL}/employees/export_csv/`, '_blank');
  };

  const handleImportCSV = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // File validation
    if (!file.name.endsWith('.csv')) {
      setImportResult({
        success: false,
        error: 'Faqat CSV fayllar ruxsat etilgan!'
      });
      return;
    }

    // File size check - 5MB max
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      setImportResult({
        success: false,
        error: 'Fayl hajmi 5MB dan oshmasligi kerak!'
      });
      return;
    }

    setImporting(true);
    setImportResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
      const response = await axios.post(`${API_BASE_URL}/employees/import_csv/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('CSV Import response:', response.data);
      setImportResult(response.data);
      loadData();
    } catch (error) {
      console.error('CSV Import error:', error);
      console.error('Error response:', error.response);
      setImportResult({
        success: false,
        error: error.response?.data?.error || error.message || 'Import qilishda xatolik yuz berdi'
      });
    } finally{
      setImporting(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
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
        <h1>Hodimlar</h1>
      </div>

      {/* Import/Export buttons */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
          <h3 style={{ margin: 0 }}>CSV Import/Export</h3>
          <div className="action-buttons">
            <button
              onClick={handleExportCSV}
              className="btn btn-primary"
              style={{ backgroundColor: '#10b981' }}
            >
              📥 CSV Eksport
            </button>
            <label className="btn btn-primary" style={{ backgroundColor: '#3b82f6', marginBottom: 0 }}>
              📤 CSV Import
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                onChange={handleImportCSV}
                style={{ display: 'none' }}
                disabled={importing}
              />
            </label>
          </div>
        </div>

        {importing && (
          <div className="alert alert-info" style={{ marginTop: '15px' }}>
            Import qilinmoqda...
          </div>
        )}

        {importResult && (
          <div className={`alert ${importResult.success ? 'alert-success' : 'alert-error'}`} style={{ marginTop: '15px' }}>
            {importResult.success ? (
              <div>
                <strong>✓ Import muvaffaqiyatli!</strong>
                <div style={{ marginTop: '5px' }}>
                  Yaratildi: {importResult.created}, Yangilandi: {importResult.updated}
                </div>
                {importResult.errors && importResult.errors.length > 0 && (
                  <div style={{ marginTop: '10px' }}>
                    <strong>Xatolar:</strong>
                    <ul style={{ marginTop: '5px', marginBottom: 0 }}>
                      {importResult.errors.map((error, index) => (
                        <li key={index}>{error}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div>
                <strong>✗ Xatolik:</strong> {importResult.error}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="data-table">
        <div className="table-header">
          <h2>Hodimlar ro'yxati</h2>
          <div className="filters-container">
            <div className="form-group">
              <select
                className="form-control"
                value={selectedDepartment}
                onChange={(e) => setSelectedDepartment(e.target.value)}
              >
                <option value="">Barcha bo'limlar</option>
                {departments.map((dept) => (
                  <option key={dept.id} value={dept.id}>
                    {dept.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <input
                type="text"
                className="form-control"
                placeholder="Qidirish..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
        </div>
        <div className="table-wrapper">
          <table>
          <thead>
            <tr>
              <th>Hodim ID</th>
              <th>F.I.O</th>
              <th>Bo'lim</th>
              <th>Lavozim</th>
              <th>Email</th>
              <th>Telefon</th>
              <th>Qurilmalar</th>
              <th>Holat</th>
            </tr>
          </thead>
          <tbody>
            {employees.length > 0 ? (
              employees.map((employee) => (
                <tr key={employee.id}>
                  <td>{employee.employee_id}</td>
                  <td>{employee.full_name}</td>
                  <td>{employee.department_name || 'N/A'}</td>
                  <td>{employee.position}</td>
                  <td>{employee.email || '-'}</td>
                  <td>{employee.phone || '-'}</td>
                  <td>
                    <span className="badge badge-warning">
                      {employee.current_equipment_count || 0}
                    </span>
                  </td>
                  <td>
                    {employee.is_active ? (
                      <span className="badge badge-success">Faol</span>
                    ) : (
                      <span className="badge badge-danger">Nofaol</span>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="8" style={{ textAlign: 'center' }}>
                  Hodimlar topilmadi
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

export default Employees;

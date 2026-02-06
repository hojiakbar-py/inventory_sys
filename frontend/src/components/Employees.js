import React, { useState, useEffect, useRef, useCallback } from 'react';
import { employeeAPI, departmentAPI, branchAPI, api } from '../api';

function Employees() {
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [branches, setBranches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('');
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [newEmployee, setNewEmployee] = useState({
    employee_id: '',
    first_name: '',
    last_name: '',
    department: '',
    branch: '',
    position: '',
    email: '',
    phone: ''
  });
  const fileInputRef = useRef(null);

  const loadData = useCallback(async () => {
    try {
      const params = {};
      if (searchTerm) params.search = searchTerm;
      if (selectedDepartment) params.department = selectedDepartment;

      const [employeesRes, departmentsRes, branchesRes] = await Promise.all([
        employeeAPI.getAll(params),
        departmentAPI.getAll(),
        branchAPI.getAll()
      ]);

      setEmployees(employeesRes.data.results || employeesRes.data);
      setDepartments(departmentsRes.data.results || departmentsRes.data);
      setBranches(branchesRes.data.results || branchesRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Ma\'lumotlarni yuklashda xatolik:', error);
      setLoading(false);
    }
  }, [searchTerm, selectedDepartment]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleExportCSV = async () => {
    try {
      const response = await api.get('/employees/export_csv/', {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'employees_export.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('CSV export xatolik:', error);
      alert('CSV eksport qilishda xatolik yuz berdi');
    }
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
      const response = await api.post('/employees/import_csv/', formData, {
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
    } finally {
      setImporting(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleAddEmployee = async (e) => {
    e.preventDefault();
    if (!newEmployee.employee_id || !newEmployee.first_name || !newEmployee.last_name) {
      alert('Hodim ID, Ism va Familiya majburiy!');
      return;
    }

    setSubmitting(true);
    try {
      await employeeAPI.create(newEmployee);
      setShowAddModal(false);
      setNewEmployee({
        employee_id: '',
        first_name: '',
        last_name: '',
        department: '',
        branch: '',
        position: '',
        email: '',
        phone: ''
      });
      loadData();
      alert('Hodim muvaffaqiyatli qo\'shildi!');
    } catch (error) {
      console.error('Add employee error:', error);
      alert(error.response?.data?.error || 'Hodim qo\'shishda xatolik yuz berdi');
    } finally {
      setSubmitting(false);
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
            <button
              onClick={() => setShowAddModal(true)}
              className="btn btn-primary"
              style={{ backgroundColor: '#8b5cf6' }}
            >
              ➕ Hodim Qo'shish
            </button>
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

      {/* Add Employee Modal */}
      {showAddModal && (
        <div className="modal-overlay" style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div className="modal-content" style={{
            backgroundColor: 'white',
            padding: '30px',
            borderRadius: '12px',
            width: '90%',
            maxWidth: '500px',
            maxHeight: '90vh',
            overflowY: 'auto'
          }}>
            <h2 style={{ marginBottom: '20px' }}>➕ Yangi Hodim Qo'shish</h2>
            <form onSubmit={handleAddEmployee}>
              <div className="form-group" style={{ marginBottom: '15px' }}>
                <label>Hodim ID *</label>
                <input
                  type="text"
                  className="form-control"
                  value={newEmployee.employee_id}
                  onChange={(e) => setNewEmployee({ ...newEmployee, employee_id: e.target.value })}
                  placeholder="Masalan: EMP001"
                  required
                />
              </div>
              <div className="form-group" style={{ marginBottom: '15px' }}>
                <label>Ism *</label>
                <input
                  type="text"
                  className="form-control"
                  value={newEmployee.first_name}
                  onChange={(e) => setNewEmployee({ ...newEmployee, first_name: e.target.value })}
                  placeholder="Ismni kiriting"
                  required
                />
              </div>
              <div className="form-group" style={{ marginBottom: '15px' }}>
                <label>Familiya *</label>
                <input
                  type="text"
                  className="form-control"
                  value={newEmployee.last_name}
                  onChange={(e) => setNewEmployee({ ...newEmployee, last_name: e.target.value })}
                  placeholder="Familiyani kiriting"
                  required
                />
              </div>
              <div className="form-group" style={{ marginBottom: '15px' }}>
                <label>Filial *</label>
                <select
                  className="form-control"
                  value={newEmployee.branch}
                  onChange={(e) => setNewEmployee({ ...newEmployee, branch: e.target.value })}
                  required
                >
                  <option value="">Filialni tanlang</option>
                  {branches.map((branch) => (
                    <option key={branch.id} value={branch.id}>{branch.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group" style={{ marginBottom: '15px' }}>
                <label>Bo'lim</label>
                <select
                  className="form-control"
                  value={newEmployee.department}
                  onChange={(e) => setNewEmployee({ ...newEmployee, department: e.target.value })}
                >
                  <option value="">Bo'limni tanlang</option>
                  {departments
                    .filter(dept => !newEmployee.branch || dept.branch === parseInt(newEmployee.branch))
                    .map((dept) => (
                      <option key={dept.id} value={dept.id}>{dept.name}</option>
                    ))}
                </select>
              </div>
              <div className="form-group" style={{ marginBottom: '15px' }}>
                <label>Lavozim</label>
                <input
                  type="text"
                  className="form-control"
                  value={newEmployee.position}
                  onChange={(e) => setNewEmployee({ ...newEmployee, position: e.target.value })}
                  placeholder="Lavozimni kiriting"
                />
              </div>
              <div className="form-group" style={{ marginBottom: '15px' }}>
                <label>Email</label>
                <input
                  type="email"
                  className="form-control"
                  value={newEmployee.email}
                  onChange={(e) => setNewEmployee({ ...newEmployee, email: e.target.value })}
                  placeholder="email@example.com"
                />
              </div>
              <div className="form-group" style={{ marginBottom: '20px' }}>
                <label>Telefon</label>
                <input
                  type="text"
                  className="form-control"
                  value={newEmployee.phone}
                  onChange={(e) => setNewEmployee({ ...newEmployee, phone: e.target.value })}
                  placeholder="+998 90 123 45 67"
                />
              </div>
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="btn"
                  style={{ backgroundColor: '#e5e7eb', color: '#374151' }}
                  disabled={submitting}
                >
                  Bekor qilish
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  style={{ backgroundColor: '#10b981' }}
                  disabled={submitting}
                >
                  {submitting ? 'Saqlanmoqda...' : 'Saqlash'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Employees;

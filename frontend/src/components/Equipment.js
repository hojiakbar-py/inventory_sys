import React, { useState, useEffect, useRef, useCallback } from 'react';
import { equipmentAPI, equipmentCategoryAPI, branchAPI, employeeAPI, departmentAPI, api } from '../api';
import { Link } from 'react-router-dom';
import InvoiceScanner from './InvoiceScanner';

function Equipment() {
  const [equipment, setEquipment] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const [showInvoiceScanner, setShowInvoiceScanner] = useState(false);
  const [scannedItems, setScannedItems] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [branches, setBranches] = useState([]);
  const [newEquipment, setNewEquipment] = useState({
    name: '',
    inventory_number: '',
    serial_number: '',
    category: '',
    branch: '',
    manufacturer: '',
    model: '',
    status: 'AVAILABLE',
    purchase_price: '',
    purchase_date: ''
  });
  const [employees, setEmployees] = useState([]);
  const [showCsvPreview, setShowCsvPreview] = useState(false);
  const [csvPreviewData, setCsvPreviewData] = useState([]);
  const [csvFile, setCsvFile] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [showAddEmployeeModal, setShowAddEmployeeModal] = useState(false);
  const [newEmployeeData, setNewEmployeeData] = useState({
    employee_id: '',
    first_name: '',
    last_name: '',
    branch: '',
    department: '',
    position: '',
  });
  const [addingEmployee, setAddingEmployee] = useState(false);
  const [showAddBranchModal, setShowAddBranchModal] = useState(false);
  const [newBranchData, setNewBranchData] = useState({ code: '', name: '', address: '', city: '' });
  const [addingBranch, setAddingBranch] = useState(false);
  const [showAddDepartmentModal, setShowAddDepartmentModal] = useState(false);
  const [newDepartmentData, setNewDepartmentData] = useState({ code: '', name: '', branch: '' });
  const [addingDepartment, setAddingDepartment] = useState(false);
  const fileInputRef = useRef(null);

  const loadData = useCallback(async () => {
    try {
      const params = {};
      if (searchTerm) params.search = searchTerm;
      if (selectedCategory) params.category = selectedCategory;
      if (selectedStatus) params.status = selectedStatus;

      const [equipmentRes, categoriesRes, branchesRes, employeesRes, departmentsRes] = await Promise.all([
        equipmentAPI.getAll(params),
        equipmentCategoryAPI.getAll(),
        branchAPI.getAll(),
        employeeAPI.getAll(),
        departmentAPI.getAll()
      ]);

      setEquipment(equipmentRes.data.results || equipmentRes.data);
      setCategories(categoriesRes.data.results || categoriesRes.data);
      setBranches(branchesRes.data.results || branchesRes.data);
      setEmployees(employeesRes.data.results || employeesRes.data);
      setDepartments(departmentsRes.data.results || departmentsRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Ma\'lumotlarni yuklashda xatolik:', error);
      setLoading(false);
    }
  }, [searchTerm, selectedCategory, selectedStatus]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const getStatusBadge = (status) => {
    const statusMap = {
      'AVAILABLE': { label: 'Mavjud', class: 'badge-success' },
      'ASSIGNED': { label: 'Tayinlangan', class: 'badge-warning' },
      'MAINTENANCE': { label: 'Ta\'mirlashda', class: 'badge-danger' },
      'RETIRED': { label: 'Chiqarilgan', class: 'badge-secondary' }
    };
    const statusInfo = statusMap[status] || { label: status, class: '' };
    return <span className={`badge ${statusInfo.class}`}>{statusInfo.label}</span>;
  };

  const handleExportCSV = async () => {
    try {
      const response = await api.get('/equipment/export_csv/', {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'equipment_export.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('CSV export xatolik:', error);
      alert('CSV eksport qilishda xatolik yuz berdi');
    }
  };

  // CSV namuna yuklab olish
  const handleDownloadTemplate = () => {
    const headers = 'inventory_number,name,category,branch,manufacturer,model,serial_number,purchase_date,purchase_price,status,condition';
    const example1 = 'INV-001,Dell XPS 15,Laptop,Bosh filial,Dell,XPS 15 9500,8H6512-AB,2024-01-15,1500.00,AVAILABLE,NEW';
    const example2 = 'INV-002,HP LaserJet Pro,Printer,Ombor,HP,M404dn,,,,ASSIGNED,GOOD';
    const example3 = 'INV-003,Samsung Monitor,Monitor,Bosh filial,Samsung,S24R350,,,,,NEW';
    const csvContent = `${headers}\n${example1}\n${example2}\n${example3}\n`;

    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'equipment_import_namuna.csv');
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  };

  // CSV faylni o'qib, preview ko'rsatish
  const handleImportCSV = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      setImportResult({ success: false, error: 'Faqat CSV fayllar ruxsat etilgan!' });
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      setImportResult({ success: false, error: 'Fayl hajmi 5MB dan oshmasligi kerak!' });
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    setCsvFile(file);

    // CSV ni o'qib, preview uchun parse qilish
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      const lines = text.split('\n').filter(line => line.trim());
      if (lines.length < 2) {
        setImportResult({ success: false, error: 'CSV fayl bo\'sh yoki noto\'g\'ri formatda!' });
        if (fileInputRef.current) fileInputRef.current.value = '';
        return;
      }

      const headers = lines[0].split(',').map(h => h.trim().replace(/^\uFEFF/, ''));
      const rows = [];

      for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',').map(v => v.trim());
        const row = {};
        headers.forEach((header, idx) => {
          row[header] = values[idx] || '';
        });
        // assigned_to va assigned_date maydonlarini bo'sh qo'shish (foydalanuvchi modal da tanlaydi)
        if (!row.assigned_to) row.assigned_to = '';
        if (!row.assigned_date) row.assigned_date = '';
        rows.push(row);
      }

      setCsvPreviewData(rows);
      setShowCsvPreview(true);
    };
    reader.readAsText(file);

    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // CSV preview dan import qilish
  const handleConfirmImport = async () => {
    if (csvPreviewData.length === 0) return;

    setShowCsvPreview(false);
    setImporting(true);
    setImportResult(null);

    // CSV ma'lumotlarini assigned_to va assigned_date bilan qayta yozish
    const headers = Object.keys(csvPreviewData[0]);
    // assigned_to va assigned_date ni headers ga qo'shish (agar yo'q bo'lsa)
    if (!headers.includes('assigned_to')) headers.push('assigned_to');
    if (!headers.includes('assigned_date')) headers.push('assigned_date');

    const csvLines = [headers.join(',')];
    csvPreviewData.forEach(row => {
      const values = headers.map(h => row[h] || '');
      csvLines.push(values.join(','));
    });
    const csvContent = csvLines.join('\n');

    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const fileName = csvFile ? csvFile.name : 'import.csv';
    const newFile = new File([blob], fileName, { type: 'text/csv' });

    const formData = new FormData();
    formData.append('file', newFile);

    try {
      const response = await api.post('/equipment/import_csv/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setImportResult(response.data);
      loadData();
    } catch (error) {
      setImportResult({
        success: false,
        error: error.response?.data?.error || error.message || 'Import qilishda xatolik yuz berdi'
      });
    } finally {
      setImporting(false);
      setCsvFile(null);
      setCsvPreviewData([]);
    }
  };

  // Preview da assigned_to o'zgartirish
  const handleAssignedToChange = (rowIndex, employeeId) => {
    const updated = [...csvPreviewData];
    updated[rowIndex].assigned_to = employeeId;
    setCsvPreviewData(updated);
  };

  // Preview da assigned_date o'zgartirish
  const handleAssignedDateChange = (rowIndex, dateValue) => {
    const updated = [...csvPreviewData];
    updated[rowIndex].assigned_date = dateValue;
    setCsvPreviewData(updated);
  };

  // Preview da statusni o'zgartirish
  const handleStatusChange = (rowIndex, newStatus) => {
    const updated = [...csvPreviewData];
    updated[rowIndex].status = newStatus;
    // Agar status ASSIGNED emas bo'lsa, assigned_to va assigned_date ni tozalash
    if (newStatus !== 'ASSIGNED' && newStatus !== 'Tayinlangan') {
      updated[rowIndex].assigned_to = '';
      updated[rowIndex].assigned_date = '';
    }
    setCsvPreviewData(updated);
  };

  // CSV Preview ichidan yangi xodim qo'shish
  const handleAddNewEmployee = async () => {
    if (!newEmployeeData.employee_id || !newEmployeeData.first_name ||
        !newEmployeeData.last_name || !newEmployeeData.branch) {
      alert('Hodim ID, Ism, Familiya va Filial majburiy!');
      return;
    }
    setAddingEmployee(true);
    try {
      await employeeAPI.create(newEmployeeData);
      // Xodimlar ro'yxatini yangilash
      const empRes = await employeeAPI.getAll();
      setEmployees(empRes.data.results || empRes.data);
      setShowAddEmployeeModal(false);
      setNewEmployeeData({
        employee_id: '', first_name: '', last_name: '',
        branch: '', department: '', position: ''
      });
      alert('Hodim muvaffaqiyatli qo\'shildi!');
    } catch (error) {
      const errData = error.response?.data;
      let errMsg = 'Hodim qo\'shishda xatolik';
      if (errData) {
        if (typeof errData === 'object') {
          errMsg = Object.entries(errData).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join('\n');
        } else {
          errMsg = errData.detail || errData;
        }
      }
      alert(errMsg);
    } finally {
      setAddingEmployee(false);
    }
  };

  // Yangi filial qo'shish
  const handleAddNewBranch = async () => {
    if (!newBranchData.code || !newBranchData.name || !newBranchData.address || !newBranchData.city) {
      alert('Kod, Nomi, Manzil va Shahar majburiy!');
      return;
    }
    setAddingBranch(true);
    try {
      await branchAPI.create(newBranchData);
      const brRes = await branchAPI.getAll();
      setBranches(brRes.data.results || brRes.data);
      setShowAddBranchModal(false);
      setNewBranchData({ code: '', name: '', address: '', city: '' });
      alert('Filial muvaffaqiyatli qo\'shildi!');
    } catch (error) {
      const errData = error.response?.data;
      let errMsg = 'Filial qo\'shishda xatolik';
      if (errData && typeof errData === 'object') {
        errMsg = Object.entries(errData).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join('\n');
      }
      alert(errMsg);
    } finally {
      setAddingBranch(false);
    }
  };

  // Yangi bo'lim qo'shish
  const handleAddNewDepartment = async () => {
    if (!newDepartmentData.code || !newDepartmentData.name || !newDepartmentData.branch) {
      alert('Kod, Nomi va Filial majburiy!');
      return;
    }
    setAddingDepartment(true);
    try {
      await departmentAPI.create(newDepartmentData);
      const depRes = await departmentAPI.getAll();
      setDepartments(depRes.data.results || depRes.data);
      setShowAddDepartmentModal(false);
      setNewDepartmentData({ code: '', name: '', branch: '' });
      alert('Bo\'lim muvaffaqiyatli qo\'shildi!');
    } catch (error) {
      const errData = error.response?.data;
      let errMsg = 'Bo\'lim qo\'shishda xatolik';
      if (errData && typeof errData === 'object') {
        errMsg = Object.entries(errData).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join('\n');
      }
      alert(errMsg);
    } finally {
      setAddingDepartment(false);
    }
  };

  const handleScanComplete = (data) => {
    console.log('Scanned invoice data:', data);
    setScannedItems(data);
    setShowInvoiceScanner(false);
  };

  const handleCreateFromScanned = async (item, index) => {
    try {
      // Generate inventory number
      const inventoryNumber = `INV-${Date.now()}-${index + 1}`;

      // Create equipment data
      const equipmentData = {
        name: item.name,
        inventory_number: inventoryNumber,
        serial_number: item.serial_numbers && item.serial_numbers.length > 0
          ? item.serial_numbers[0]
          : `SN-${inventoryNumber}`,
        manufacturer: item.manufacturer || '',
        model: item.model || '',
        purchase_price: item.price || 0,
        status: 'AVAILABLE',
        purchase_date: new Date().toISOString().split('T')[0],
        warranty_expiry: item.warranty_months
          ? new Date(Date.now() + item.warranty_months * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
          : null,
        notes: item.description || '',
      };

      await equipmentAPI.create(equipmentData);

      // Remove item from scanned list
      const updatedItems = { ...scannedItems };
      updatedItems.items = updatedItems.items.filter((_, i) => i !== index);
      setScannedItems(updatedItems.items.length > 0 ? updatedItems : null);

      // Reload equipment list
      loadData();

      setImportResult({
        success: true,
        created: 1,
        updated: 0,
        errors: []
      });
    } catch (error) {
      console.error('Create equipment error:', error);
      setImportResult({
        success: false,
        error: error.response?.data?.error || 'Qurilma qo\'shishda xatolik yuz berdi'
      });
    }
  };

  const handleAddEquipment = async (e) => {
    e.preventDefault();
    if (!newEquipment.name) {
      alert('Qurilma nomi majburiy!');
      return;
    }

    setSubmitting(true);
    try {
      await equipmentAPI.create(newEquipment);
      setShowAddModal(false);
      setNewEquipment({
        name: '',
        inventory_number: '',
        serial_number: '',
        category: '',
        branch: '',
        manufacturer: '',
        model: '',
        status: 'AVAILABLE',
        purchase_price: '',
        purchase_date: ''
      });
      loadData();
      alert('Qurilma muvaffaqiyatli qo\'shildi!');
    } catch (error) {
      console.error('Add equipment error:', error);
      alert(error.response?.data?.error || 'Qurilma qo\'shishda xatolik yuz berdi');
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
        <h1>Qurilmalar</h1>
      </div>

      {/* Import/Export buttons */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
          <h3 style={{ margin: 0 }}>Import/Export</h3>
          <div className="action-buttons">
            <button
              onClick={handleDownloadTemplate}
              className="btn btn-primary"
              style={{ backgroundColor: '#6366f1' }}
            >
              📋 Namuna yuklab olish
            </button>
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
              onClick={() => setShowInvoiceScanner(true)}
              className="btn btn-primary"
              style={{ backgroundColor: '#8b5cf6' }}
            >
              📄 Nakladnoy Skanerlash
            </button>
            <button
              onClick={() => setShowAddModal(true)}
              className="btn btn-primary"
              style={{ backgroundColor: '#f59e0b' }}
            >
              ➕ Qurilma Qo'shish
            </button>
          </div>
        </div>

        <div style={{ marginTop: '10px', padding: '10px', backgroundColor: '#f0f9ff', borderRadius: '6px', fontSize: '13px', color: '#475569' }}>
          <strong>CSV formati:</strong> inventory_number, name, category, branch, manufacturer, model, serial_number, purchase_date, purchase_price, status, condition
          <br />
          <span style={{ color: '#64748b' }}>
            * serial_number, purchase_date, purchase_price — ixtiyoriy (bo'sh qolsa "N/A" bo'ladi)
            <br />
            * Agar status "Tayinlangan" bo'lsa, import vaqtida hodimni tanlash oynasi chiqadi.
          </span>
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
          <h2>Qurilmalar ro'yxati</h2>
          <div className="filters-container">
            <div className="form-group">
              <select
                className="form-control"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                <option value="">Barcha kategoriyalar</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <select
                className="form-control"
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
              >
                <option value="">Barcha holatlar</option>
                <option value="AVAILABLE">Mavjud</option>
                <option value="ASSIGNED">Tayinlangan</option>
                <option value="MAINTENANCE">Ta'mirlashda</option>
                <option value="RETIRED">Chiqarilgan</option>
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
                <th>Inventar #</th>
                <th>Nomi</th>
                <th>Kategoriya</th>
                <th>Ishlab chiqaruvchi</th>
                <th>Model</th>
                <th>Holati</th>
                <th>Joriy foydalanuvchi</th>
                <th>Amallar</th>
              </tr>
            </thead>
            <tbody>
              {equipment.length > 0 ? (
                equipment.map((item) => (
                  <tr key={item.id}>
                    <td>{item.inventory_number}</td>
                    <td>{item.name}</td>
                    <td>{item.category_name || 'N/A'}</td>
                    <td>{item.manufacturer || '-'}</td>
                    <td>{item.model || '-'}</td>
                    <td>{getStatusBadge(item.status)}</td>
                    <td>
                      {item.current_assignment ? (
                        <div>
                          <strong>{item.current_assignment.employee}</strong>
                          <br />
                          <small>{item.current_assignment.department || ''}</small>
                          <br />
                          <small style={{ color: '#888' }}>
                            {item.current_assignment.days_assigned} kun
                          </small>
                        </div>
                      ) : (
                        '-'
                      )}
                    </td>
                    <td>
                      <Link to={`/equipment/${item.id}`} className="btn btn-primary" style={{ fontSize: '12px', padding: '5px 10px' }}>
                        Batafsil
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center' }}>
                    Qurilmalar topilmadi
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Invoice Scanner Modal */}
      {showInvoiceScanner && (
        <InvoiceScanner
          onScanComplete={handleScanComplete}
          onClose={() => setShowInvoiceScanner(false)}
        />
      )}

      {/* Scanned Items Display */}
      {scannedItems && scannedItems.items && scannedItems.items.length > 0 && (
        <div className="card" style={{ marginTop: '20px' }}>
          <h3 style={{ marginBottom: '20px' }}>📄 Nakladnoydan Olingan Ma'lumotlar</h3>
          <p style={{ color: '#666', marginBottom: '20px' }}>
            Quyidagi qurilmalarni tasdiqlang va bazaga qo'shing:
          </p>

          <div style={{ display: 'grid', gap: '15px' }}>
            {scannedItems.items.map((item, index) => (
              <div
                key={index}
                style={{
                  border: '2px solid #e0e0e0',
                  borderRadius: '8px',
                  padding: '15px',
                  backgroundColor: '#f9f9f9'
                }}
              >
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '10px',
                  marginBottom: '15px'
                }}>
                  <div>
                    <strong>Nomi:</strong><br />
                    {item.name}
                  </div>
                  <div>
                    <strong>Miqdor:</strong><br />
                    {item.quantity}
                  </div>
                  <div>
                    <strong>Narx:</strong><br />
                    {item.price ? item.price.toLocaleString('uz-UZ') + ' so\'m' : 'N/A'}
                  </div>
                  {item.manufacturer && (
                    <div>
                      <strong>Ishlab chiqaruvchi:</strong><br />
                      {item.manufacturer}
                    </div>
                  )}
                  {item.model && (
                    <div>
                      <strong>Model:</strong><br />
                      {item.model}
                    </div>
                  )}
                  {item.warranty_months && (
                    <div>
                      <strong>Kafolat:</strong><br />
                      {item.warranty_months} oy
                    </div>
                  )}
                  {item.serial_numbers && item.serial_numbers.length > 0 && (
                    <div>
                      <strong>Seriya raqamlari:</strong><br />
                      {item.serial_numbers.join(', ')}
                    </div>
                  )}
                </div>

                <button
                  onClick={() => handleCreateFromScanned(item, index)}
                  className="btn btn-primary"
                  style={{
                    backgroundColor: '#10b981',
                    padding: '8px 16px',
                    fontSize: '14px'
                  }}
                >
                  ✓ Bazaga Qo'shish
                </button>
              </div>
            ))}
          </div>

          <button
            onClick={() => setScannedItems(null)}
            style={{
              marginTop: '20px',
              padding: '10px 20px',
              border: '2px solid #e0e0e0',
              borderRadius: '6px',
              backgroundColor: 'white',
              color: '#666',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 'bold'
            }}
          >
            Yopish
          </button>
        </div>
      )}

      {/* CSV Preview Modal */}
      {showCsvPreview && (
        <div className="modal-overlay" style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
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
            width: '95%',
            maxWidth: '1000px',
            maxHeight: '90vh',
            overflowY: 'auto'
          }}>
            <h2 style={{ marginBottom: '10px' }}>📋 CSV Import — Ko'rib chiqish</h2>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              {csvPreviewData.length} ta qurilma topildi. "Tayinlangan" statusli qurilmalar uchun hodimni tanlang.
            </p>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f1f5f9' }}>
                    <th style={{ padding: '8px', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>#</th>
                    <th style={{ padding: '8px', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>Inventar #</th>
                    <th style={{ padding: '8px', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>Nomi</th>
                    <th style={{ padding: '8px', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>Kategoriya</th>
                    <th style={{ padding: '8px', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>Status</th>
                    <th style={{ padding: '8px', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>Tayinlangan hodim</th>
                    <th style={{ padding: '8px', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>Qachondan beri?</th>
                  </tr>
                </thead>
                <tbody>
                  {csvPreviewData.map((row, index) => {
                    const isAssigned = row.status === 'ASSIGNED' || row.status === 'Tayinlangan';
                    const needsEmployee = isAssigned && !row.assigned_to;
                    return (
                      <tr
                        key={index}
                        style={{
                          backgroundColor: needsEmployee ? '#fef2f2' : (index % 2 === 0 ? 'white' : '#f8fafc'),
                          borderBottom: '1px solid #e2e8f0'
                        }}
                      >
                        <td style={{ padding: '8px' }}>{index + 1}</td>
                        <td style={{ padding: '8px', fontWeight: 'bold' }}>{row.inventory_number || '-'}</td>
                        <td style={{ padding: '8px' }}>{row.name || '-'}</td>
                        <td style={{ padding: '8px' }}>{row.category || '-'}</td>
                        <td style={{ padding: '8px' }}>
                          <select
                            value={row.status || 'AVAILABLE'}
                            onChange={(e) => handleStatusChange(index, e.target.value)}
                            style={{
                              padding: '4px 8px',
                              borderRadius: '4px',
                              border: '1px solid #d1d5db',
                              fontSize: '12px',
                              backgroundColor: isAssigned ? '#fef3c7' : '#ecfdf5'
                            }}
                          >
                            <option value="AVAILABLE">Mavjud</option>
                            <option value="ASSIGNED">Tayinlangan</option>
                            <option value="MAINTENANCE">Ta'mirlashda</option>
                            <option value="RETIRED">Chiqarilgan</option>
                          </select>
                        </td>
                        <td style={{ padding: '8px' }}>
                          {isAssigned ? (
                            <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                              <select
                                value={row.assigned_to || ''}
                                onChange={(e) => handleAssignedToChange(index, e.target.value)}
                                style={{
                                  padding: '4px 8px',
                                  borderRadius: '4px',
                                  border: needsEmployee ? '2px solid #ef4444' : '1px solid #d1d5db',
                                  fontSize: '12px',
                                  backgroundColor: needsEmployee ? '#fef2f2' : 'white',
                                  minWidth: '180px',
                                  flex: 1
                                }}
                              >
                                <option value="">-- Hodimni tanlang --</option>
                                {employees.map((emp) => (
                                  <option key={emp.id} value={emp.employee_id}>
                                    {emp.employee_id} — {emp.first_name} {emp.last_name}
                                  </option>
                                ))}
                              </select>
                              <button
                                type="button"
                                onClick={() => setShowAddEmployeeModal(true)}
                                style={{
                                  padding: '4px 8px',
                                  fontSize: '14px',
                                  backgroundColor: '#10b981',
                                  color: 'white',
                                  border: 'none',
                                  borderRadius: '4px',
                                  cursor: 'pointer',
                                  whiteSpace: 'nowrap',
                                  lineHeight: '1'
                                }}
                                title="Yangi hodim qo'shish"
                              >
                                +
                              </button>
                            </div>
                          ) : (
                            <span style={{ color: '#9ca3af', fontSize: '12px' }}>—</span>
                          )}
                        </td>
                        <td style={{ padding: '8px' }}>
                          {isAssigned ? (
                            <input
                              type="date"
                              value={row.assigned_date || ''}
                              onChange={(e) => handleAssignedDateChange(index, e.target.value)}
                              max={new Date().toISOString().split('T')[0]}
                              style={{
                                padding: '4px 8px',
                                borderRadius: '4px',
                                border: '1px solid #d1d5db',
                                fontSize: '12px'
                              }}
                              placeholder="Bo'sh = bugun"
                            />
                          ) : (
                            <span style={{ color: '#9ca3af', fontSize: '12px' }}>—</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Ogohlantirish — tayinlanmagan qurilmalar */}
            {csvPreviewData.some(row =>
              (row.status === 'ASSIGNED' || row.status === 'Tayinlangan') && !row.assigned_to
            ) && (
              <div style={{
                marginTop: '15px',
                padding: '12px',
                backgroundColor: '#fef2f2',
                borderRadius: '6px',
                border: '1px solid #fecaca',
                color: '#991b1b',
                fontSize: '13px'
              }}>
                ⚠️ Ba'zi "Tayinlangan" statusli qurilmalar uchun hodim tanlanmagan.
                Agar hodim tanlamasangiz, status avtomatik "Mavjud" ga o'zgartiriladi.
              </div>
            )}

            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '20px' }}>
              <button
                onClick={() => {
                  setShowCsvPreview(false);
                  setCsvPreviewData([]);
                  setCsvFile(null);
                }}
                className="btn"
                style={{ backgroundColor: '#e5e7eb', color: '#374151' }}
              >
                Bekor qilish
              </button>
              <button
                onClick={handleConfirmImport}
                className="btn btn-primary"
                style={{ backgroundColor: '#10b981' }}
              >
                ✓ Import qilish ({csvPreviewData.length} ta qurilma)
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Employee Modal (CSV Preview ichidan) */}
      {showAddEmployeeModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.6)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 2000
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '25px',
            width: '90%',
            maxWidth: '500px',
            maxHeight: '90vh',
            overflowY: 'auto',
            boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ margin: 0, color: '#1e293b' }}>Yangi Hodim Qo'shish</h3>
              <button
                onClick={() => setShowAddEmployeeModal(false)}
                style={{
                  background: 'none', border: 'none', fontSize: '24px',
                  cursor: 'pointer', color: '#64748b'
                }}
              >
                ×
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: '600', fontSize: '14px', color: '#374151' }}>
                  Hodim ID <span style={{ color: '#ef4444' }}>*</span>
                </label>
                <input
                  type="text"
                  value={newEmployeeData.employee_id}
                  onChange={(e) => setNewEmployeeData({...newEmployeeData, employee_id: e.target.value})}
                  placeholder="Masalan: EMP-005"
                  style={{
                    width: '100%', padding: '8px 12px', borderRadius: '6px',
                    border: '1px solid #d1d5db', fontSize: '14px', boxSizing: 'border-box'
                  }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '4px', fontWeight: '600', fontSize: '14px', color: '#374151' }}>
                    Ism <span style={{ color: '#ef4444' }}>*</span>
                  </label>
                  <input
                    type="text"
                    value={newEmployeeData.first_name}
                    onChange={(e) => setNewEmployeeData({...newEmployeeData, first_name: e.target.value})}
                    placeholder="Ism"
                    style={{
                      width: '100%', padding: '8px 12px', borderRadius: '6px',
                      border: '1px solid #d1d5db', fontSize: '14px', boxSizing: 'border-box'
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '4px', fontWeight: '600', fontSize: '14px', color: '#374151' }}>
                    Familiya <span style={{ color: '#ef4444' }}>*</span>
                  </label>
                  <input
                    type="text"
                    value={newEmployeeData.last_name}
                    onChange={(e) => setNewEmployeeData({...newEmployeeData, last_name: e.target.value})}
                    placeholder="Familiya"
                    style={{
                      width: '100%', padding: '8px 12px', borderRadius: '6px',
                      border: '1px solid #d1d5db', fontSize: '14px', boxSizing: 'border-box'
                    }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: '600', fontSize: '14px', color: '#374151' }}>
                  Filial <span style={{ color: '#ef4444' }}>*</span>
                </label>
                <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                  <select
                    value={newEmployeeData.branch}
                    onChange={(e) => setNewEmployeeData({...newEmployeeData, branch: e.target.value, department: ''})}
                    style={{
                      flex: 1, padding: '8px 12px', borderRadius: '6px',
                      border: '1px solid #d1d5db', fontSize: '14px', boxSizing: 'border-box'
                    }}
                  >
                    <option value="">-- Filialni tanlang --</option>
                    {branches.map((b) => (
                      <option key={b.id} value={b.id}>{b.name}</option>
                    ))}
                  </select>
                  <button
                    type="button"
                    onClick={() => setShowAddBranchModal(true)}
                    style={{
                      padding: '8px 12px', fontSize: '16px', backgroundColor: '#10b981',
                      color: 'white', border: 'none', borderRadius: '6px',
                      cursor: 'pointer', lineHeight: '1', fontWeight: 'bold'
                    }}
                    title="Yangi filial qo'shish"
                  >
                    +
                  </button>
                </div>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: '600', fontSize: '14px', color: '#374151' }}>
                  Bo'lim
                </label>
                <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                  <select
                    value={newEmployeeData.department}
                    onChange={(e) => setNewEmployeeData({...newEmployeeData, department: e.target.value})}
                    style={{
                      flex: 1, padding: '8px 12px', borderRadius: '6px',
                      border: '1px solid #d1d5db', fontSize: '14px', boxSizing: 'border-box'
                    }}
                  >
                    <option value="">-- Bo'limni tanlang --</option>
                    {departments
                      .filter((d) => !newEmployeeData.branch || String(d.branch) === String(newEmployeeData.branch))
                      .map((d) => (
                        <option key={d.id} value={d.id}>{d.name}</option>
                      ))
                    }
                  </select>
                  <button
                    type="button"
                    onClick={() => {
                      if (newEmployeeData.branch) {
                        setNewDepartmentData({...newDepartmentData, branch: newEmployeeData.branch});
                      }
                      setShowAddDepartmentModal(true);
                    }}
                    style={{
                      padding: '8px 12px', fontSize: '16px', backgroundColor: '#10b981',
                      color: 'white', border: 'none', borderRadius: '6px',
                      cursor: 'pointer', lineHeight: '1', fontWeight: 'bold'
                    }}
                    title="Yangi bo'lim qo'shish"
                  >
                    +
                  </button>
                </div>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: '600', fontSize: '14px', color: '#374151' }}>
                  Lavozim
                </label>
                <input
                  type="text"
                  value={newEmployeeData.position}
                  onChange={(e) => setNewEmployeeData({...newEmployeeData, position: e.target.value})}
                  placeholder="Masalan: Dasturchi"
                  style={{
                    width: '100%', padding: '8px 12px', borderRadius: '6px',
                    border: '1px solid #d1d5db', fontSize: '14px', boxSizing: 'border-box'
                  }}
                />
              </div>
            </div>

            <div style={{ display: 'flex', gap: '10px', marginTop: '20px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setShowAddEmployeeModal(false)}
                style={{
                  padding: '8px 20px', borderRadius: '6px', border: '1px solid #d1d5db',
                  backgroundColor: 'white', cursor: 'pointer', fontSize: '14px'
                }}
              >
                Bekor qilish
              </button>
              <button
                onClick={handleAddNewEmployee}
                disabled={addingEmployee}
                style={{
                  padding: '8px 20px', borderRadius: '6px', border: 'none',
                  backgroundColor: addingEmployee ? '#9ca3af' : '#10b981',
                  color: 'white', cursor: addingEmployee ? 'not-allowed' : 'pointer',
                  fontSize: '14px', fontWeight: '600'
                }}
              >
                {addingEmployee ? 'Saqlanmoqda...' : 'Saqlash'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Branch Modal */}
      {showAddBranchModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.6)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 3000
        }}>
          <div style={{
            backgroundColor: 'white', borderRadius: '12px', padding: '25px',
            width: '90%', maxWidth: '450px', boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ margin: 0, color: '#1e293b' }}>Yangi Filial Qo'shish</h3>
              <button
                onClick={() => setShowAddBranchModal(false)}
                style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', color: '#64748b' }}
              >
                x
              </button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: '600', fontSize: '14px', color: '#374151' }}>
                  Kod <span style={{ color: '#ef4444' }}>*</span>
                </label>
                <input
                  type="text" value={newBranchData.code}
                  onChange={(e) => setNewBranchData({...newBranchData, code: e.target.value})}
                  placeholder="Masalan: BR-003"
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px', boxSizing: 'border-box' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: '600', fontSize: '14px', color: '#374151' }}>
                  Nomi <span style={{ color: '#ef4444' }}>*</span>
                </label>
                <input
                  type="text" value={newBranchData.name}
                  onChange={(e) => setNewBranchData({...newBranchData, name: e.target.value})}
                  placeholder="Masalan: Yangiyo'l filiali"
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px', boxSizing: 'border-box' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: '600', fontSize: '14px', color: '#374151' }}>
                  Manzil <span style={{ color: '#ef4444' }}>*</span>
                </label>
                <input
                  type="text" value={newBranchData.address}
                  onChange={(e) => setNewBranchData({...newBranchData, address: e.target.value})}
                  placeholder="Masalan: Amir Temur ko'chasi 15"
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px', boxSizing: 'border-box' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: '600', fontSize: '14px', color: '#374151' }}>
                  Shahar <span style={{ color: '#ef4444' }}>*</span>
                </label>
                <input
                  type="text" value={newBranchData.city}
                  onChange={(e) => setNewBranchData({...newBranchData, city: e.target.value})}
                  placeholder="Masalan: Toshkent"
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px', boxSizing: 'border-box' }}
                />
              </div>
            </div>
            <div style={{ display: 'flex', gap: '10px', marginTop: '20px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setShowAddBranchModal(false)}
                style={{ padding: '8px 20px', borderRadius: '6px', border: '1px solid #d1d5db', backgroundColor: 'white', cursor: 'pointer', fontSize: '14px' }}
              >
                Bekor qilish
              </button>
              <button
                onClick={handleAddNewBranch} disabled={addingBranch}
                style={{
                  padding: '8px 20px', borderRadius: '6px', border: 'none',
                  backgroundColor: addingBranch ? '#9ca3af' : '#10b981',
                  color: 'white', cursor: addingBranch ? 'not-allowed' : 'pointer',
                  fontSize: '14px', fontWeight: '600'
                }}
              >
                {addingBranch ? 'Saqlanmoqda...' : 'Saqlash'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Department Modal */}
      {showAddDepartmentModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.6)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 3000
        }}>
          <div style={{
            backgroundColor: 'white', borderRadius: '12px', padding: '25px',
            width: '90%', maxWidth: '450px', boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ margin: 0, color: '#1e293b' }}>Yangi Bo'lim Qo'shish</h3>
              <button
                onClick={() => setShowAddDepartmentModal(false)}
                style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', color: '#64748b' }}
              >
                x
              </button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: '600', fontSize: '14px', color: '#374151' }}>
                  Kod <span style={{ color: '#ef4444' }}>*</span>
                </label>
                <input
                  type="text" value={newDepartmentData.code}
                  onChange={(e) => setNewDepartmentData({...newDepartmentData, code: e.target.value})}
                  placeholder="Masalan: DEP-IT"
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px', boxSizing: 'border-box' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: '600', fontSize: '14px', color: '#374151' }}>
                  Nomi <span style={{ color: '#ef4444' }}>*</span>
                </label>
                <input
                  type="text" value={newDepartmentData.name}
                  onChange={(e) => setNewDepartmentData({...newDepartmentData, name: e.target.value})}
                  placeholder="Masalan: IT bo'limi"
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px', boxSizing: 'border-box' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: '600', fontSize: '14px', color: '#374151' }}>
                  Filial <span style={{ color: '#ef4444' }}>*</span>
                </label>
                <select
                  value={newDepartmentData.branch}
                  onChange={(e) => setNewDepartmentData({...newDepartmentData, branch: e.target.value})}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px', boxSizing: 'border-box' }}
                >
                  <option value="">-- Filialni tanlang --</option>
                  {branches.map((b) => (
                    <option key={b.id} value={b.id}>{b.name}</option>
                  ))}
                </select>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '10px', marginTop: '20px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setShowAddDepartmentModal(false)}
                style={{ padding: '8px 20px', borderRadius: '6px', border: '1px solid #d1d5db', backgroundColor: 'white', cursor: 'pointer', fontSize: '14px' }}
              >
                Bekor qilish
              </button>
              <button
                onClick={handleAddNewDepartment} disabled={addingDepartment}
                style={{
                  padding: '8px 20px', borderRadius: '6px', border: 'none',
                  backgroundColor: addingDepartment ? '#9ca3af' : '#10b981',
                  color: 'white', cursor: addingDepartment ? 'not-allowed' : 'pointer',
                  fontSize: '14px', fontWeight: '600'
                }}
              >
                {addingDepartment ? 'Saqlanmoqda...' : 'Saqlash'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Equipment Modal */}
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
            maxWidth: '600px',
            maxHeight: '90vh',
            overflowY: 'auto'
          }}>
            <h2 style={{ marginBottom: '20px' }}>➕ Yangi Qurilma Qo'shish</h2>
            <form onSubmit={handleAddEquipment}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div className="form-group">
                  <label>Qurilma nomi *</label>
                  <input
                    type="text"
                    className="form-control"
                    value={newEquipment.name}
                    onChange={(e) => setNewEquipment({ ...newEquipment, name: e.target.value })}
                    placeholder="Masalan: Dell Monitor"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Inventar raqami</label>
                  <input
                    type="text"
                    className="form-control"
                    value={newEquipment.inventory_number}
                    onChange={(e) => setNewEquipment({ ...newEquipment, inventory_number: e.target.value })}
                    placeholder="Bo'sh qoldirsangiz avtomatik yaratiladi"
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginTop: '15px' }}>
                <div className="form-group">
                  <label>Seriya raqami</label>
                  <input
                    type="text"
                    className="form-control"
                    value={newEquipment.serial_number}
                    onChange={(e) => setNewEquipment({ ...newEquipment, serial_number: e.target.value })}
                    placeholder="Masalan: SN123456"
                  />
                </div>
                <div className="form-group">
                  <label>Filial *</label>
                  <select
                    className="form-control"
                    value={newEquipment.branch}
                    onChange={(e) => setNewEquipment({ ...newEquipment, branch: e.target.value })}
                    required
                  >
                    <option value="">Filialni tanlang</option>
                    {branches.map((branch) => (
                      <option key={branch.id} value={branch.id}>{branch.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginTop: '15px' }}>
                <div className="form-group">
                  <label>Kategoriya</label>
                  <select
                    className="form-control"
                    value={newEquipment.category}
                    onChange={(e) => setNewEquipment({ ...newEquipment, category: e.target.value })}
                  >
                    <option value="">Kategoriyani tanlang</option>
                    {categories.map((cat) => (
                      <option key={cat.id} value={cat.id}>{cat.name}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Ishlab chiqaruvchi</label>
                  <input
                    type="text"
                    className="form-control"
                    value={newEquipment.manufacturer}
                    onChange={(e) => setNewEquipment({ ...newEquipment, manufacturer: e.target.value })}
                    placeholder="Masalan: Dell, HP, Lenovo"
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginTop: '15px' }}>
                <div className="form-group">
                  <label>Model</label>
                  <input
                    type="text"
                    className="form-control"
                    value={newEquipment.model}
                    onChange={(e) => setNewEquipment({ ...newEquipment, model: e.target.value })}
                    placeholder="Masalan: U2422H"
                  />
                </div>
                <div className="form-group">
                  <label>Holat</label>
                  <select
                    className="form-control"
                    value={newEquipment.status}
                    onChange={(e) => setNewEquipment({ ...newEquipment, status: e.target.value })}
                  >
                    <option value="AVAILABLE">Mavjud</option>
                    <option value="ASSIGNED">Tayinlangan</option>
                    <option value="MAINTENANCE">Ta'mirlashda</option>
                    <option value="RETIRED">Chiqarilgan</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginTop: '15px' }}>
                <div className="form-group">
                  <label>Xarid narxi</label>
                  <input
                    type="number"
                    className="form-control"
                    value={newEquipment.purchase_price}
                    onChange={(e) => setNewEquipment({ ...newEquipment, purchase_price: e.target.value })}
                    placeholder="0"
                  />
                </div>
                <div className="form-group">
                  <label>Xarid sanasi</label>
                  <input
                    type="date"
                    className="form-control"
                    value={newEquipment.purchase_date}
                    onChange={(e) => setNewEquipment({ ...newEquipment, purchase_date: e.target.value })}
                  />
                </div>
              </div>
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '20px' }}>
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
        </div >
      )
      }
    </div >
  );
}

export default Equipment;

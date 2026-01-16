import React, { useState, useEffect, useRef } from 'react';
import { equipmentAPI, equipmentCategoryAPI } from '../api';
import { Link } from 'react-router-dom';
import axios from 'axios';
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
  const fileInputRef = useRef(null);

  useEffect(() => {
    loadData();
  }, [searchTerm, selectedCategory, selectedStatus]);

  const loadData = async () => {
    try {
      const params = {};
      if (searchTerm) params.search = searchTerm;
      if (selectedCategory) params.category = selectedCategory;
      if (selectedStatus) params.status = selectedStatus;

      const [equipmentRes, categoriesRes] = await Promise.all([
        equipmentAPI.getAll(params),
        equipmentCategoryAPI.getAll()
      ]);

      setEquipment(equipmentRes.data.results || equipmentRes.data);
      setCategories(categoriesRes.data.results || categoriesRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Ma\'lumotlarni yuklashda xatolik:', error);
      setLoading(false);
    }
  };

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

  const handleExportCSV = () => {
    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    window.open(`${API_BASE_URL}/equipment/export_csv/`, '_blank');
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
      const response = await axios.post(`${API_BASE_URL}/equipment/import_csv/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('CSV Import response:', response.data);
      setImportResult(response.data);
      loadData(); // Reload data after import
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
                        <small style={{color: '#888'}}>
                          {item.current_assignment.days_assigned} kun
                        </small>
                      </div>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td>
                    <Link to={`/equipment/${item.id}`} className="btn btn-primary" style={{fontSize: '12px', padding: '5px 10px'}}>
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
                    <strong>Nomi:</strong><br/>
                    {item.name}
                  </div>
                  <div>
                    <strong>Miqdor:</strong><br/>
                    {item.quantity}
                  </div>
                  <div>
                    <strong>Narx:</strong><br/>
                    {item.price ? item.price.toLocaleString('uz-UZ') + ' so\'m' : 'N/A'}
                  </div>
                  {item.manufacturer && (
                    <div>
                      <strong>Ishlab chiqaruvchi:</strong><br/>
                      {item.manufacturer}
                    </div>
                  )}
                  {item.model && (
                    <div>
                      <strong>Model:</strong><br/>
                      {item.model}
                    </div>
                  )}
                  {item.warranty_months && (
                    <div>
                      <strong>Kafolat:</strong><br/>
                      {item.warranty_months} oy
                    </div>
                  )}
                  {item.serial_numbers && item.serial_numbers.length > 0 && (
                    <div>
                      <strong>Seriya raqamlari:</strong><br/>
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
    </div>
  );
}

export default Equipment;

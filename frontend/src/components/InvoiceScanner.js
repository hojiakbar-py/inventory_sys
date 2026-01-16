import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';

function InvoiceScanner() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleImageUpload = (event) => {
    const file = event.target.files[0];

    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      setError('Faqat JPG, PNG yoki WEBP rasm fayllar ruxsat etilgan!');
      return;
    }

    // Validate file size (max 4MB)
    const maxSize = 4 * 1024 * 1024;
    if (file.size > maxSize) {
      setError('Rasm hajmi 4MB dan oshmasligi kerak!');
      return;
    }

    setImage(file);
    setPreview(URL.createObjectURL(file));
    setError(null);
    setResult(null);
  };

  const handleScan = async () => {
    if (!image) {
      setError('Iltimos, avval rasm yuklang!');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', image);

    try {
      const response = await api.post('/equipment/scan_invoice_gemini/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.success) {
        console.log('Gemini response:', response.data.data);
        setResult(response.data.data);
        setError(null);
      } else {
        setError(response.data.error || 'Xatolik yuz berdi');
      }
    } catch (err) {
      console.error('Scan error:', err);
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else {
        setError('Serverga ulanishda xatolik. Iltimos, qayta urinib ko\'ring.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAddToInventory = async () => {
    if (!result || !result.items || result.items.length === 0) {
      setError('Qo\'shiladigan mahsulotlar yo\'q!');
      return;
    }

    setLoading(true);

    try {
      const createdItems = [];

      // Map category names to standard categories (matching existing DB categories)
      const categoryMapping = {
        'клавиатура': 'Klaviaturalar',
        'keyboard': 'Klaviaturalar',
        'kompyuter aksessuari': 'Klaviaturalar', // Generic accessories
        'мышь': 'Sichqonchalar',
        'mouse': 'Sichqonchalar',
        'монитор': 'Monitorlar',
        'monitor': 'Monitorlar',
        'ноутбук': 'Noutbuklar',
        'notebook': 'Noutbuklar',
        'laptop': 'Noutbuklar',
        'компьютер': 'Laptop', // Use Laptop category for computers
        'computer': 'Laptop',
        'kompyuter': 'Laptop',
        'принтер': 'Printerlar',
        'printer': 'Printerlar',
        'сканер': 'Proyektorlar',
        'scanner': 'Proyektorlar',
        'телефон': 'Telefonlar',
        'phone': 'Telefonlar',
        'планшет': 'Planshetlar',
        'tablet': 'Planshetlar',
        'проектор': 'Proyektorlar',
        'projector': 'Proyektorlar',
        'сервер': 'Serverlar',
        'server': 'Serverlar',
        'камера': 'Kameralar',
        'camera': 'Kameralar'
      };

      for (const item of result.items) {
        // Get or create category
        let categoryId = null;
        try {
          // Normalize category name
          const normalizedCategory = item.category?.toLowerCase() || 'boshqa';
          const categoryName = categoryMapping[normalizedCategory] || item.category || 'Boshqa';

          const categoriesResponse = await api.get('/equipment-categories/', {
            params: { search: categoryName }
          });

          if (categoriesResponse.data.results && categoriesResponse.data.results.length > 0) {
            categoryId = categoriesResponse.data.results[0].id;
          } else {
            // Create new category
            const categoryData = {
              name: categoryName,
              code: categoryName.substring(0, 10).toUpperCase()
            };
            const newCategory = await api.post('/equipment-categories/', categoryData);
            categoryId = newCategory.data.id;
          }
        } catch (err) {
          console.error('Category error:', err);
        }

        // Create equipment for each quantity
        const quantity = item.quantity || 1;
        for (let i = 0; i < quantity; i++) {
          // Generate unique inventory number
          const timestamp = Date.now();
          const randomSuffix = Math.random().toString(36).substring(2, 6).toUpperCase();
          const inventoryNumber = `INV-${timestamp}-${randomSuffix}`;

          // Ensure purchase_date is a string, not array
          let purchaseDate = result.invoice_date || new Date().toISOString().split('T')[0];
          if (Array.isArray(purchaseDate)) {
            purchaseDate = purchaseDate[0] || new Date().toISOString().split('T')[0];
          }

          const equipmentData = {
            name: item.name,
            category: categoryId,
            inventory_number: inventoryNumber,
            serial_number: item.serial_number || '',
            manufacturer: item.manufacturer || '',
            model: item.model || '',
            purchase_price: item.price || 0,
            purchase_date: purchaseDate,
            status: 'AVAILABLE',
            description: `Nakladnoy dan import qilingan (${result.supplier || 'Google Gemini AI'})`
          };

          console.log('Creating equipment:', equipmentData);

          // Calculate warranty expiry
          if (item.warranty_months) {
            const warrantyDate = new Date();
            warrantyDate.setMonth(warrantyDate.getMonth() + parseInt(item.warranty_months));
            equipmentData.warranty_expiry = warrantyDate.toISOString().split('T')[0];
          }

          try {
            const response = await api.post('/equipment/', equipmentData);
            createdItems.push(response.data);
          } catch (err) {
            console.error('Equipment create error:', err);
          }
        }
      }

      alert(`✅ ${createdItems.length} ta qurilma muvaffaqiyatli qo'shildi!`);
      navigate('/equipment');

    } catch (err) {
      console.error('Add to inventory error:', err);
      setError('Bazaga qo\'shishda xatolik yuz berdi');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setImage(null);
    setPreview(null);
    setResult(null);
    setError(null);
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '30px', textAlign: 'center' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '10px', color: '#1976d2' }}>
          📄 Nakladnoy Scanner
        </h1>
        <p style={{ color: '#666', fontSize: '1.1rem' }}>
          Google Gemini AI bilan nakladnoy rasmidan avtomatik ma'lumot olish (100% BEPUL!)
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <div style={{
          backgroundColor: '#ffebee',
          color: '#c62828',
          padding: '15px 20px',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '1px solid #ef5350'
        }}>
          <strong>❌ Xatolik:</strong> {error}
        </div>
      )}

      {/* Main Content */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        padding: '30px',
        marginBottom: '30px'
      }}>
        <h3 style={{ marginTop: 0 }}>1️⃣ Nakladnoy rasmini yuklang</h3>

        {/* Upload Area */}
        {!preview ? (
          <div style={{
            border: '3px dashed #2196f3',
            borderRadius: '12px',
            padding: '60px 40px',
            textAlign: 'center',
            backgroundColor: '#f0f9ff',
            cursor: 'pointer',
            transition: 'all 0.3s ease'
          }}>
            <label htmlFor="image-upload" style={{ cursor: 'pointer', display: 'block' }}>
              <div style={{ fontSize: '4rem', marginBottom: '20px' }}>📸</div>
              <p style={{ fontSize: '1.2rem', color: '#1976d2', fontWeight: 'bold', marginBottom: '10px' }}>
                Rasm yuklash uchun bosing yoki faylni bu yerga torting
              </p>
              <p style={{ color: '#666', margin: 0 }}>
                JPG, PNG, WEBP (max 4MB)
              </p>
              <input
                id="image-upload"
                type="file"
                accept="image/jpeg,image/jpg,image/png,image/webp"
                onChange={handleImageUpload}
                style={{ display: 'none' }}
              />
            </label>
          </div>
        ) : (
          <div>
            <div style={{
              border: '2px solid #e0e0e0',
              borderRadius: '12px',
              padding: '20px',
              textAlign: 'center',
              backgroundColor: '#fafafa'
            }}>
              <img
                src={preview}
                alt="Nakladnoy preview"
                style={{
                  maxWidth: '100%',
                  maxHeight: '500px',
                  borderRadius: '8px',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                }}
              />
            </div>
            <button
              onClick={handleReset}
              style={{
                marginTop: '15px',
                padding: '10px 20px',
                backgroundColor: '#f44336',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '1rem',
                fontWeight: 'bold'
              }}
            >
              🗑️ Yangi rasm yuklash
            </button>
          </div>
        )}

        {/* Scan Button */}
        {image && !result && (
          <button
            onClick={handleScan}
            disabled={loading}
            style={{
              marginTop: '20px',
              padding: '15px 40px',
              backgroundColor: loading ? '#ccc' : '#2196f3',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '1.1rem',
              fontWeight: 'bold',
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '10px'
            }}
          >
            {loading ? (
              <>
                <span style={{
                  width: '20px',
                  height: '20px',
                  border: '3px solid white',
                  borderTopColor: 'transparent',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite',
                  display: 'inline-block'
                }}></span>
                <span>Google Gemini AI tahlil qilyapti...</span>
              </>
            ) : (
              <>🔍 Nakladnoyni skanerlash</>
            )}
          </button>
        )}
      </div>

      {/* Result Section */}
      {result && (
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
          padding: '30px',
          marginBottom: '30px'
        }}>
          <h3 style={{ marginTop: 0, color: '#4caf50' }}>✅ 2️⃣ Topilgan mahsulotlar</h3>

          {/* Invoice Info */}
          <div style={{
            backgroundColor: '#f0f9ff',
            padding: '20px',
            borderRadius: '8px',
            marginBottom: '25px',
            border: '1px solid #2196f3'
          }}>
            {result.invoice_date && (
              <div style={{ marginBottom: '10px' }}>
                <strong>📅 Sana:</strong> {result.invoice_date}
              </div>
            )}
            {result.supplier && (
              <div style={{ marginBottom: '10px' }}>
                <strong>🏢 Yetkazib beruvchi:</strong> {result.supplier}
              </div>
            )}
            <div>
              <strong>🤖 AI Model:</strong> Google Gemini 1.5 Flash ⚡ (BEPUL!)
            </div>
          </div>

          {/* Items List */}
          <div style={{ marginBottom: '25px' }}>
            {result.items && result.items.map((item, index) => (
              <div key={index} style={{
                border: '2px solid #e0e0e0',
                borderRadius: '10px',
                padding: '20px',
                marginBottom: '15px',
                backgroundColor: '#fafafa'
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '15px'
                }}>
                  <h4 style={{ margin: 0, color: '#1976d2', fontSize: '1.2rem' }}>
                    {item.name}
                  </h4>
                  <span style={{
                    backgroundColor: '#2196f3',
                    color: 'white',
                    padding: '5px 15px',
                    borderRadius: '20px',
                    fontWeight: 'bold'
                  }}>
                    ×{item.quantity || 1}
                  </span>
                </div>

                <div style={{ lineHeight: '1.8' }}>
                  {item.manufacturer && (
                    <div><strong>🏭 Ishlab chiqaruvchi:</strong> {item.manufacturer}</div>
                  )}
                  {item.model && (
                    <div><strong>📦 Model:</strong> {item.model}</div>
                  )}
                  {item.serial_number && (
                    <div><strong>🔢 Seriya:</strong> {item.serial_number}</div>
                  )}
                  {item.category && (
                    <div><strong>📂 Kategoriya:</strong> {item.category}</div>
                  )}
                  {item.price > 0 && (
                    <div><strong>💰 Narxi:</strong> {item.price.toLocaleString()} so'm</div>
                  )}
                  {item.warranty_months && (
                    <div><strong>🛡️ Kafolat:</strong> {item.warranty_months} oy</div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
            <button
              onClick={handleAddToInventory}
              disabled={loading}
              style={{
                flex: 1,
                padding: '15px 30px',
                backgroundColor: loading ? '#ccc' : '#4caf50',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: '1.1rem',
                fontWeight: 'bold'
              }}
            >
              {loading ? '⏳ Qo\'shilmoqda...' : '✅ Barcha mahsulotlarni bazaga qo\'shish'}
            </button>

            <button
              onClick={handleReset}
              style={{
                padding: '15px 30px',
                backgroundColor: '#ff9800',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '1.1rem',
                fontWeight: 'bold'
              }}
            >
              🔄 Boshqatan boshlash
            </button>
          </div>
        </div>
      )}

      {/* Help Section */}
      <div style={{
        backgroundColor: '#f0f9ff',
        borderRadius: '12px',
        padding: '30px',
        border: '1px solid #2196f3'
      }}>
        <h3 style={{ marginTop: 0 }}>💡 Qanday ishlaydi?</h3>
        <ol style={{ lineHeight: '2', fontSize: '1.05rem' }}>
          <li>Nakladnoy rasmini telefon yoki skanerdan oling</li>
          <li>Rasmni yuklab, "Skanerlash" tugmasini bosing</li>
          <li>Google Gemini AI nakladnoydan ma'lumotlarni avtomatik o'qiydi</li>
          <li>Natijalarni tekshiring va bazaga qo'shing</li>
        </ol>

        <div style={{ marginTop: '20px' }}>
          <h4 style={{ color: '#1976d2' }}>📌 Maslahatlar:</h4>
          <ul style={{ lineHeight: '2' }}>
            <li>✅ Rasmni yaxshi yoritilgan joyda oling</li>
            <li>✅ Matnlar aniq ko'rinishi kerak</li>
            <li>✅ Nakladnoyning to'liq ko'rinishi bo'lishi kerak</li>
            <li>✅ JPG, PNG yoki WEBP formatda yuklang</li>
            <li>✅ Rasm hajmi 4MB dan oshmasligi kerak</li>
          </ul>
        </div>
      </div>

      {/* CSS Animation */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default InvoiceScanner;

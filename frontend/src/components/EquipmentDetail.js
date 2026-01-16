import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { equipmentAPI, employeeAPI, maintenanceAPI } from '../api';

function EquipmentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [equipment, setEquipment] = useState(null);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAssignForm, setShowAssignForm] = useState(false);
  const [showReturnForm, setShowReturnForm] = useState(false);
  const [showInventoryForm, setShowInventoryForm] = useState(false);
  const [showMaintenanceForm, setShowMaintenanceForm] = useState(false);

  const [assignData, setAssignData] = useState({
    employee_id: '',
    condition: '',
    notes: ''
  });

  const [returnData, setReturnData] = useState({
    condition: '',
    notes: ''
  });

  const [inventoryData, setInventoryData] = useState({
    location: '',
    condition: '',
    is_functional: true,
    notes: '',
    employee_confirmed: false
  });

  const [maintenanceData, setMaintenanceData] = useState({
    maintenance_type: 'REPAIR',
    description: '',
    performed_by: '',
    cost: 0,
    notes: ''
  });

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      const [equipmentRes, employeesRes] = await Promise.all([
        equipmentAPI.get(id),
        employeeAPI.getAll()
      ]);
      setEquipment(equipmentRes.data);
      setEmployees(employeesRes.data.results || employeesRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Ma\'lumotlarni yuklashda xatolik:', error);
      setLoading(false);
    }
  };

  const handleAssign = async (e) => {
    e.preventDefault();
    try {
      await equipmentAPI.assign(id, assignData);
      alert('Qurilma muvaffaqiyatli tayinlandi!');
      setShowAssignForm(false);
      loadData();
    } catch (error) {
      alert('Xatolik: ' + (error.response?.data?.error || 'Tayinlashda xatolik'));
    }
  };

  const handleReturn = async (e) => {
    e.preventDefault();
    try {
      await equipmentAPI.returnEquipment(id, returnData);
      alert('Qurilma muvaffaqiyatli qaytarildi!');
      setShowReturnForm(false);
      loadData();
    } catch (error) {
      alert('Xatolik: ' + (error.response?.data?.error || 'Qaytarishda xatolik'));
    }
  };

  const handleInventoryCheck = async (e) => {
    e.preventDefault();
    try {
      await equipmentAPI.inventoryCheck(id, inventoryData);
      alert('Inventarizatsiya tekshiruvi muvaffaqiyatli saqlandi!');
      setShowInventoryForm(false);
      loadData();
    } catch (error) {
      alert('Xatolik: ' + (error.response?.data?.error || 'Saqlashda xatolik'));
    }
  };

  const handleMaintenance = async (e) => {
    e.preventDefault();
    try {
      await maintenanceAPI.create({ ...maintenanceData, equipment: id });
      alert('Ta\'mirlash yozuvi muvaffaqiyatli saqlandi!');
      setShowMaintenanceForm(false);
      loadData();
    } catch (error) {
      alert('Xatolik: Saqlashda xatolik');
    }
  };

  if (loading) {
    return <div className="loading">Yuklanmoqda...</div>;
  }

  if (!equipment) {
    return <div className="error">Qurilma topilmadi</div>;
  }

  return (
    <div>
      <div className="page-header">
        <h1>{equipment.name}</h1>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn btn-secondary" onClick={() => navigate('/equipment')}>
            ← Orqaga
          </button>
        </div>
      </div>

      <div className="form-container">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div>
            <h3>Asosiy Ma'lumotlar</h3>
            <p><strong>Inventar #:</strong> {equipment.inventory_number}</p>
            <p><strong>Seriya #:</strong> {equipment.serial_number}</p>
            <p><strong>Kategoriya:</strong> {equipment.category_name || 'N/A'}</p>
            <p><strong>Ishlab chiqaruvchi:</strong> {equipment.manufacturer || 'N/A'}</p>
            <p><strong>Model:</strong> {equipment.model || 'N/A'}</p>
            <p><strong>Holati:</strong> {equipment.status}</p>
          </div>
          <div>
            <h3>Moliyaviy Ma'lumotlar</h3>
            {equipment.purchase_date && (
              <p><strong>Xarid sanasi:</strong> {new Date(equipment.purchase_date).toLocaleDateString('uz-UZ')}</p>
            )}
            {equipment.purchase_price && (
              <p><strong>Xarid narxi:</strong> {equipment.purchase_price} so'm</p>
            )}
            {equipment.warranty_expiry && (
              <p><strong>Kafolat muddati:</strong> {new Date(equipment.warranty_expiry).toLocaleDateString('uz-UZ')}</p>
            )}
          </div>
        </div>

        {equipment.description && (
          <div style={{ marginTop: '20px' }}>
            <h3>Tavsif</h3>
            <p>{equipment.description}</p>
          </div>
        )}

        {equipment.qr_code && (
          <div style={{
            marginTop: '30px',
            textAlign: 'center',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderRadius: '16px',
            padding: '30px',
            boxShadow: '0 10px 30px rgba(0,0,0,0.15)',
            position: 'relative',
            overflow: 'hidden'
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

            <h3 style={{
              color: 'white',
              marginBottom: '20px',
              fontSize: '24px',
              fontWeight: '600',
              textShadow: '0 2px 4px rgba(0,0,0,0.2)',
              position: 'relative',
              zIndex: 1
            }}>QR Kod</h3>

            <div style={{
              background: 'white',
              borderRadius: '16px',
              padding: '20px',
              display: 'inline-block',
              boxShadow: '0 8px 25px rgba(0,0,0,0.2)',
              position: 'relative',
              zIndex: 1
            }}>
              <img
                src={equipment.qr_code}
                alt="QR Code"
                style={{
                  width: '250px',
                  height: '250px',
                  display: 'block'
                }}
              />
            </div>

            <p style={{
              marginTop: '20px',
              fontSize: '13px',
              color: 'rgba(255,255,255,0.9)',
              fontFamily: 'monospace',
              background: 'rgba(0,0,0,0.2)',
              padding: '8px 16px',
              borderRadius: '8px',
              display: 'inline-block',
              position: 'relative',
              zIndex: 1
            }}>
              EQUIPMENT:{equipment.inventory_number}
            </p>
          </div>
        )}
      </div>

      {equipment.current_assignment && (
        <div className="form-container" style={{ marginTop: '20px', backgroundColor: '#e8f5e9' }}>
          <h3 style={{ color: '#2e7d32' }}>📍 Hozirgi Tayinlash</h3>
          <p><strong>Hodim:</strong> {equipment.current_assignment.employee}</p>
          <p><strong>Hodim ID:</strong> {equipment.current_assignment.employee_id}</p>
          <p><strong>Bo'lim:</strong> {equipment.current_assignment.department || 'N/A'}</p>
          <p><strong>Tayinlangan:</strong> {new Date(equipment.current_assignment.assigned_date).toLocaleDateString('uz-UZ')}</p>
          <p><strong>Muddat:</strong> {equipment.current_assignment.days_assigned} kun</p>
          <button className="btn btn-danger" onClick={() => setShowReturnForm(!showReturnForm)}>
            Qaytarib Olish
          </button>
        </div>
      )}

      <div style={{ marginTop: '20px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        {!equipment.current_assignment && equipment.status === 'AVAILABLE' && (
          <button className="btn btn-success" onClick={() => setShowAssignForm(!showAssignForm)}>
            Hodimga Tayinlash
          </button>
        )}
        <button className="btn btn-primary" onClick={() => setShowInventoryForm(!showInventoryForm)}>
          Inventarizatsiya Tekshiruvi
        </button>
        <button className="btn btn-warning" onClick={() => setShowMaintenanceForm(!showMaintenanceForm)}>
          Ta'mirlash Yozuvi
        </button>
      </div>

      {showAssignForm && (
        <div className="form-container" style={{ marginTop: '20px' }}>
          <h3>Hodimga Tayinlash</h3>
          <form onSubmit={handleAssign}>
            <div className="form-group">
              <label>Hodim *</label>
              <select
                value={assignData.employee_id}
                onChange={(e) => setAssignData({ ...assignData, employee_id: e.target.value })}
                required
              >
                <option value="">Hodimni tanlang</option>
                {employees.map(emp => (
                  <option key={emp.id} value={emp.id}>
                    {emp.full_name} ({emp.employee_id}) - {emp.department_name || 'N/A'}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Holat *</label>
              <input
                type="text"
                value={assignData.condition}
                onChange={(e) => setAssignData({ ...assignData, condition: e.target.value })}
                placeholder="Masalan: Yaxshi holatda"
                required
              />
            </div>
            <div className="form-group">
              <label>Izoh</label>
              <textarea
                value={assignData.notes}
                onChange={(e) => setAssignData({ ...assignData, notes: e.target.value })}
              />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-success">Tayinlash</button>
              <button type="button" className="btn btn-danger" onClick={() => setShowAssignForm(false)}>
                Bekor qilish
              </button>
            </div>
          </form>
        </div>
      )}

      {showReturnForm && (
        <div className="form-container" style={{ marginTop: '20px' }}>
          <h3>Qaytarib Olish</h3>
          <form onSubmit={handleReturn}>
            <div className="form-group">
              <label>Qaytarish paytidagi holat *</label>
              <input
                type="text"
                value={returnData.condition}
                onChange={(e) => setReturnData({ ...returnData, condition: e.target.value })}
                placeholder="Masalan: Yaxshi holatda"
                required
              />
            </div>
            <div className="form-group">
              <label>Izoh</label>
              <textarea
                value={returnData.notes}
                onChange={(e) => setReturnData({ ...returnData, notes: e.target.value })}
              />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-danger">Qaytarib Olish</button>
              <button type="button" className="btn btn-secondary" onClick={() => setShowReturnForm(false)}>
                Bekor qilish
              </button>
            </div>
          </form>
        </div>
      )}

      {showInventoryForm && (
        <div className="form-container" style={{ marginTop: '20px' }}>
          <h3>Inventarizatsiya Tekshiruvi</h3>
          <form onSubmit={handleInventoryCheck}>
            <div className="form-group">
              <label>Joylashuv *</label>
              <input
                type="text"
                value={inventoryData.location}
                onChange={(e) => setInventoryData({ ...inventoryData, location: e.target.value })}
                placeholder="Masalan: Bino A, 3-qavat, 301"
                required
              />
            </div>
            <div className="form-group">
              <label>Holat *</label>
              <textarea
                value={inventoryData.condition}
                onChange={(e) => setInventoryData({ ...inventoryData, condition: e.target.value })}
                placeholder="Qurilma holati haqida"
                required
              />
            </div>
            <div className="form-group">
              <label style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <input
                  type="checkbox"
                  checked={inventoryData.is_functional}
                  onChange={(e) => setInventoryData({ ...inventoryData, is_functional: e.target.checked })}
                  style={{ width: 'auto' }}
                />
                Ishlayaptimi?
              </label>
            </div>
            <div className="form-group">
              <label style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <input
                  type="checkbox"
                  checked={inventoryData.employee_confirmed}
                  onChange={(e) => setInventoryData({ ...inventoryData, employee_confirmed: e.target.checked })}
                  style={{ width: 'auto' }}
                />
                Hodim tasdiqladi
              </label>
            </div>
            <div className="form-group">
              <label>Izoh</label>
              <textarea
                value={inventoryData.notes}
                onChange={(e) => setInventoryData({ ...inventoryData, notes: e.target.value })}
              />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary">Saqlash</button>
              <button type="button" className="btn btn-danger" onClick={() => setShowInventoryForm(false)}>
                Bekor qilish
              </button>
            </div>
          </form>
        </div>
      )}

      {showMaintenanceForm && (
        <div className="form-container" style={{ marginTop: '20px' }}>
          <h3>Ta'mirlash Yozuvi</h3>
          <form onSubmit={handleMaintenance}>
            <div className="form-group">
              <label>Turi *</label>
              <select
                value={maintenanceData.maintenance_type}
                onChange={(e) => setMaintenanceData({ ...maintenanceData, maintenance_type: e.target.value })}
                required
              >
                <option value="REPAIR">Ta'mirlash</option>
                <option value="UPGRADE">Yangilash</option>
                <option value="CLEANING">Tozalash</option>
                <option value="INSPECTION">Tekshiruv</option>
              </select>
            </div>
            <div className="form-group">
              <label>Tavsif *</label>
              <textarea
                value={maintenanceData.description}
                onChange={(e) => setMaintenanceData({ ...maintenanceData, description: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Bajargan *</label>
              <input
                type="text"
                value={maintenanceData.performed_by}
                onChange={(e) => setMaintenanceData({ ...maintenanceData, performed_by: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Xarajat (so'm)</label>
              <input
                type="number"
                value={maintenanceData.cost}
                onChange={(e) => setMaintenanceData({ ...maintenanceData, cost: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>Izoh</label>
              <textarea
                value={maintenanceData.notes}
                onChange={(e) => setMaintenanceData({ ...maintenanceData, notes: e.target.value })}
              />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-warning">Saqlash</button>
              <button type="button" className="btn btn-danger" onClick={() => setShowMaintenanceForm(false)}>
                Bekor qilish
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

export default EquipmentDetail;

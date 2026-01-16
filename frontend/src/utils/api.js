import axios from 'axios';

// Smart API URL detection
// If accessing from localhost/127.0.0.1, use localhost API
// Otherwise, use the computer's IP address for mobile access
const getApiBaseUrl = () => {
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }

  const hostname = window.location.hostname;

  // If accessing from localhost or 127.0.0.1, use localhost API
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000/api';
  }

  // If accessing from IP address (mobile), use the same IP for API
  return `http://${hostname}:8000/api`;
};

const API_BASE_URL = getApiBaseUrl();

// Axios instance yaratish
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minut - AI tahlil uchun ko'proq vaqt kerak
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - har bir so'rovda token qo'shish
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - xatolarni handle qilish
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // Server javob qaytardi lekin xatolik bor
      switch (error.response.status) {
        case 401:
          // Unauthorized - tokenni tozalash va login sahifasiga yo'naltirish
          localStorage.removeItem('authToken');
          window.location.href = '/login';
          break;
        case 403:
          console.error('Ruxsat yo\'q');
          break;
        case 404:
          console.error('Topilmadi');
          break;
        case 500:
          console.error('Server xatosi');
          break;
        default:
          console.error('Xatolik yuz berdi:', error.response.data);
      }
    } else if (error.request) {
      // So'rov yuborildi lekin javob kelmadi
      console.error('Server javob bermadi. Internetni tekshiring.');
    } else {
      // Boshqa xatoliklar
      console.error('Xatolik:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;

// API funksiyalari
export const apiService = {
  // Departments
  getDepartments: () => api.get('/departments/'),
  getDepartment: (id) => api.get(`/departments/${id}/`),
  createDepartment: (data) => api.post('/departments/', data),
  updateDepartment: (id, data) => api.put(`/departments/${id}/`, data),
  deleteDepartment: (id) => api.delete(`/departments/${id}/`),

  // Employees
  getEmployees: (params) => api.get('/employees/', { params }),
  getEmployee: (id) => api.get(`/employees/${id}/`),
  createEmployee: (data) => api.post('/employees/', data),
  updateEmployee: (id, data) => api.put(`/employees/${id}/`, data),
  deleteEmployee: (id) => api.delete(`/employees/${id}/`),
  exportEmployees: () => api.get('/employees/export_csv/', { responseType: 'blob' }),

  // Equipment
  getEquipment: (params) => api.get('/equipment/', { params }),
  getEquipmentDetail: (id) => api.get(`/equipment/${id}/`),
  createEquipment: (data) => api.post('/equipment/', data),
  updateEquipment: (id, data) => api.put(`/equipment/${id}/`, data),
  deleteEquipment: (id) => api.delete(`/equipment/${id}/`),
  assignEquipment: (id, data) => api.post(`/equipment/${id}/assign/`, data),
  returnEquipment: (id, data) => api.post(`/equipment/${id}/return_equipment/`, data),
  inventoryCheck: (id, data) => api.post(`/equipment/${id}/inventory_check/`, data),
  scanEquipment: (id) => api.get(`/equipment/${id}/scan/`),

  // Equipment Categories
  getCategories: () => api.get('/equipment-categories/'),
  getCategory: (id) => api.get(`/equipment-categories/${id}/`),

  // Assignments
  getAssignments: (params) => api.get('/assignments/', { params }),
  getAssignment: (id) => api.get(`/assignments/${id}/`),
  getDashboardStats: () => api.get('/assignments/dashboard_stats/'),

  // Inventory Checks
  getInventoryChecks: (params) => api.get('/inventory-checks/', { params }),
  getInventoryCheck: (id) => api.get(`/inventory-checks/${id}/`),
  createInventoryCheck: (data) => api.post('/inventory-checks/', data),

  // Maintenance Records
  getMaintenanceRecords: (params) => api.get('/maintenance-records/', { params }),
  getMaintenanceRecord: (id) => api.get(`/maintenance-records/${id}/`),
  createMaintenanceRecord: (data) => api.post('/maintenance-records/', data),

  // QR Scan
  scanQR: (qrData) => api.post('/qr-scan/scan/', { qr_data: qrData }),
};

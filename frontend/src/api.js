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

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to all requests
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

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // Server responded with error status
      switch (error.response.status) {
        case 401:
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
          console.error('Xatolik:', error.response.data);
      }
    } else if (error.request) {
      // Request was sent but no response received (network error)
      console.error('Tarmoq xatosi. Internet aloqasini tekshiring.');
      error.message = 'Tarmoq xatosi. Serverga ulanib bo\'lmadi.';
    } else {
      // Something else happened
      console.error('Xatolik:', error.message);
    }
    return Promise.reject(error);
  }
);

export const departmentAPI = {
  getAll: () => api.get('/departments/'),
  get: (id) => api.get(`/departments/${id}/`),
  create: (data) => api.post('/departments/', data),
  update: (id, data) => api.put(`/departments/${id}/`, data),
  delete: (id) => api.delete(`/departments/${id}/`),
};

export const employeeAPI = {
  getAll: (params) => api.get('/employees/', { params }),
  get: (id) => api.get(`/employees/${id}/`),
  create: (data) => api.post('/employees/', data),
  update: (id, data) => api.put(`/employees/${id}/`, data),
  delete: (id) => api.delete(`/employees/${id}/`),
};

export const equipmentCategoryAPI = {
  getAll: () => api.get('/equipment-categories/'),
  get: (id) => api.get(`/equipment-categories/${id}/`),
  create: (data) => api.post('/equipment-categories/', data),
  update: (id, data) => api.put(`/equipment-categories/${id}/`, data),
  delete: (id) => api.delete(`/equipment-categories/${id}/`),
};

export const equipmentAPI = {
  getAll: (params) => api.get('/equipment/', { params }),
  get: (id) => api.get(`/equipment/${id}/`),
  create: (data) => api.post('/equipment/', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  update: (id, data) => api.put(`/equipment/${id}/`, data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  delete: (id) => api.delete(`/equipment/${id}/`),
  assign: (id, data) => api.post(`/equipment/${id}/assign/`, data),
  returnEquipment: (id, data) => api.post(`/equipment/${id}/return_equipment/`, data),
  inventoryCheck: (id, data) => api.post(`/equipment/${id}/inventory_check/`, data),
  scan: (id) => api.get(`/equipment/${id}/scan/`),
  scanInvoice: (formData) => api.post('/equipment/scan_invoice/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
};

export const assignmentAPI = {
  getAll: (params) => api.get('/assignments/', { params }),
  get: (id) => api.get(`/assignments/${id}/`),
  create: (data) => api.post('/assignments/', data),
  getDashboardStats: () => api.get('/assignments/dashboard_stats/'),
};

export const inventoryCheckAPI = {
  getAll: (params) => api.get('/inventory-checks/', { params }),
  get: (id) => api.get(`/inventory-checks/${id}/`),
  create: (data) => api.post('/inventory-checks/', data),
};

export const maintenanceAPI = {
  getAll: (params) => api.get('/maintenance-records/', { params }),
  get: (id) => api.get(`/maintenance-records/${id}/`),
  create: (data) => api.post('/maintenance-records/', data),
};

export const qrScanAPI = {
  scan: (qrData) => api.post('/qr-scan/scan/', { qr_data: qrData }),
};

export default api;

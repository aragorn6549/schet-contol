import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для добавления токена
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Интерцептор для обработки ошибок авторизации
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: (login: string, password: string) =>
    api.post('/api/auth/login', null, { params: { login, password } }),
  register: (data: { login: string; password: string }) =>
    api.post('/api/auth/register', data),
  getMe: () => api.get('/api/auth/me'),
};

export const profilesApi = {
  getAll: () => api.get('/api/profiles/'),
  update: (id: number, data: { full_name?: string; role?: string }) =>
    api.put(`/api/profiles/${id}`, data),
};

export const counterpartiesApi = {
  getAll: (params?: { status_filter?: string }) =>
    api.get('/api/counterparties/', { params }),
  getById: (id: number) => api.get(`/api/counterparties/${id}`),
  create: (data: any) => api.post('/api/counterparties/', data),
  updateStatus: (id: number, status: string) =>
    api.put(`/api/counterparties/${id}/status`, { status }),
};

export const requestsApi = {
  getAll: (params?: { status_filter?: string }) =>
    api.get('/api/requests/', { params }),
  getById: (id: number) => api.get(`/api/requests/${id}`),
  create: (data: any) => api.post('/api/requests/', data),
  approve: (id: number, approve: boolean) =>
    api.put(`/api/requests/${id}/approve`, null, { params: { approve } }),
  pay: (id: number) => api.put(`/api/requests/${id}/pay`),
  getPpText: (id: number) => api.get(`/api/requests/${id}/pp-text`),
};

export const journalApi = {
  getAll: (params?: { entity_type?: string }) =>
    api.get('/api/journal/', { params }),
};

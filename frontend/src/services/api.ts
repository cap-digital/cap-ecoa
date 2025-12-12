import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  register: (data: {
    email: string;
    password: string;
    full_name: string;
    political_name?: string;
    party?: string;
    state?: string;
  }) => api.post("/auth/register", data),

  login: (email: string, password: string) =>
    api.post("/auth/login", { email, password }),

  logout: () => api.post("/auth/logout"),

  getMe: () => api.get("/auth/me"),

  updateMe: (data: {
    full_name?: string;
    political_name?: string;
    party?: string;
    state?: string;
  }) => api.put("/auth/me", data),
};

// News API
export const newsApi = {
  list: (params?: {
    term?: string;
    source?: string;
    sentiment?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
    per_page?: number;
  }) => api.get("/news", { params }),

  get: (id: string) => api.get(`/news/${id}`),

  getSources: () => api.get("/news/sources/list"),
};

// Filters API
export const filtersApi = {
  list: () => api.get("/filters"),

  create: (term: string) => api.post("/filters", { term, is_active: true }),

  update: (id: string, data: { term?: string; is_active?: boolean }) =>
    api.put(`/filters/${id}`, data),

  delete: (id: string) => api.delete(`/filters/${id}`),
};

// Dashboard API
export const dashboardApi = {
  getStats: () => api.get("/dashboard/stats"),

  getTrends: (days?: number) => api.get("/dashboard/trends", { params: { days } }),

  getSources: () => api.get("/dashboard/sources"),

  getAll: () => api.get("/dashboard"),
};

import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL,
  timeout: 20000,
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    
    // Don't add token to auth endpoints (login/signup)
    const isAuthEndpoint = config.url?.includes('/auth/login') || 
                          config.url?.includes('/auth/signup');
    
    if (token && !isAuthEndpoint) {
      // Add token as query parameter (as expected by backend get_current_user)
      config.params = {
        ...config.params,
        token: token
      };
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;
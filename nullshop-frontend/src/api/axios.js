import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_URL,
});

//Перехватчик запросов
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

//Перехватчик ответов
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    //Если 401 и это не повторный запрос и не сам запрос логина/рефреша
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url.includes('/users/token') &&
      !originalRequest.url.includes('/users/refresh-token')
    ) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');

      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_URL}/users/refresh-token`, {
            refresh_token: refreshToken,
          });

          const newAccessToken = data.access_token;
          localStorage.setItem('access_token', newAccessToken);
          if (data.refresh_token) {
            localStorage.setItem('refresh_token', data.refresh_token);
          }

          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Если и refresh_token истек — разлогиниваем
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/auth';
          return Promise.reject(refreshError);
        }
      }
    }

    return Promise.reject(error);
  }
);

export default api;
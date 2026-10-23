import { create } from 'zustand';
import api from '../api/axios';

const useAuthStore = create((set, get) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,

  //Получение профиля текущего пользователя (GET /users/me)
  fetchMe: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ user: null, isAuthenticated: false });
      return;
    }

    set({ isLoading: true });
    try {
      const { data } = await api.get('/users/me');
      set({ user: data, isAuthenticated: true });
    } catch (error) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      set({ user: null, isAuthenticated: false });
    } finally {
      set({ isLoading: false });
    }
  },

  //Вход (POST /users/token через FormData / URLSearchParams)
  login: async (email, password) => {
    set({ isLoading: true });
    try {
      const formData = new URLSearchParams();
      formData.append('username', email); //FastAPI OAuth2 ждет поле username
      formData.append('password', password);

      const { data } = await api.post('/users/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      localStorage.setItem('access_token', data.access_token);
      if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token);
      }

      await get().fetchMe();
      return { success: true };
    } catch (error) {
      const message =
        error.response?.data?.detail || 'Неверный email или пароль';
      return { success: false, message };
    } finally {
      set({ isLoading: false });
    }
  },

  //Регистрация (POST /users через JSON) и автоматический вход
  register: async (email, password, role = 'buyer') => {
    set({ isLoading: true });
    try {
      await api.post('/users', { email, password, role });
      //Сразу логиним пользователя после успешной регистрации
      return await get().login(email, password);
    } catch (error) {
      let message = 'Ошибка при регистрации';
      const detail = error.response?.data?.detail;
      if (typeof detail === 'string') {
        message = detail;
      } else if (Array.isArray(detail)) {
        message = detail[0]?.msg || 'Проверьте правильность введенных данных';
      }
      return { success: false, message };
    } finally {
      set({ isLoading: false });
    }
  },

  //Выход из аккаунта
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, isAuthenticated: false });
  },
}));

export default useAuthStore;
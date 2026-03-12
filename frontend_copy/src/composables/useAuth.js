import { reactive, readonly } from 'vue';
import api from '../utils/api';

const state = reactive({
  user: localStorage.getItem('username') || null,
  roles: JSON.parse(localStorage.getItem('roles')) || [],
  isAuthenticated: localStorage.getItem('LoggedIn') === 'true',
  isLoading: false,
  error: null,
});

export function useAuth() {
  const login = async (usr, pwd) => {
    state.isLoading = true;
    state.error = null;

    try {
      // Call your custom Python method
      const response = await api.post('/intern_test.api.get_token', { usr, pwd });
      const data = response.data.message;

      // 1. Update State
      state.user = data.username;
      state.roles = data.roles;
      state.isAuthenticated = data.LoggedIn;

      // 2. Persist to LocalStorage
      localStorage.setItem('api_key', data.api_key);
      localStorage.setItem('api_secret', data.api_secret);
      localStorage.setItem('username', data.username);
      localStorage.setItem('roles', JSON.stringify(data.roles));
      localStorage.setItem('LoggedIn', 'true');

      // 3. Attach headers for all future requests
      api.defaults.headers.common['Authorization'] = `token ${data.api_key}:${data.api_secret}`;

      return true;
    } catch (err) {
      state.error = err.response?.data?.exception || 'Invalid credentials';
      return false;
    } finally {
      state.isLoading = false;
    }
  };

  const logout = () => {
    state.user = null;
    state.roles = [];
    state.isAuthenticated = false;

    localStorage.clear();
    delete api.defaults.headers.common['Authorization'];
  };

  return { state: readonly(state), login, logout };
}

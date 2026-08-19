import { api } from '../api';
import type { SignupRequest, LoginRequest, AuthResponse, User } from '../types/auth';

const TOKEN_KEY = 'cropmandi_auth_token';

export const authService = {
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  },

  setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token);
  },

  removeToken(): void {
    localStorage.removeItem(TOKEN_KEY);
  },

  async signup(data: SignupRequest): Promise<AuthResponse> {
    const res = await api.post<AuthResponse>('/auth/signup', data);
    if (res.data.access_token) {
      this.setToken(res.data.access_token);
    }
    return res.data;
  },

  async login(data: LoginRequest): Promise<AuthResponse> {
    const res = await api.post<AuthResponse>('/auth/login', data);
    if (res.data.access_token) {
      this.setToken(res.data.access_token);
    }
    return res.data;
  },

  async getCurrentUser(): Promise<User> {
    const res = await api.get<User>('/auth/me');
    return res.data;
  },

  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout');
    } catch {
      // Ignore network errors on logout
    } finally {
      this.removeToken();
    }
  }
};

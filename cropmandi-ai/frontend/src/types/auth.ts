export interface UserProfile {
  id: string;
  email: string;
  full_name?: string | null;
  phone?: string | null;
  preferred_language?: string;
  state?: string | null;
  district?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface User {
  id: string;
  email: string;
  role: 'farmer' | 'admin';
  is_active: boolean;
  profile?: UserProfile | null;
  created_at?: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  confirm_password?: string;
  full_name?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  message?: string;
  user: User;
  access_token: string;
  token_type?: string;
}

export interface AuthState {
  user: User | null;
  profile: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface AuthError {
  detail: string;
  code?: string;
  errors?: Record<string, string[]>;
}

export interface PasswordRuleCheck {
  hasMinLength: boolean;
  hasUppercase: boolean;
  hasSymbol: boolean;
  hasNoSpaces: boolean;
  passwordsMatch: boolean;
  isValid: boolean;
}

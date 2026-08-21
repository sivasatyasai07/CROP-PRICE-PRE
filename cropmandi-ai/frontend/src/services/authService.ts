import { supabase } from '../lib/supabase';
import type { SignupRequest, LoginRequest, AuthResponse, User, UserProfile } from '../types/auth';

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

  /**
   * Helper to format a Supabase auth user + profile into app User model
   */
  mapSupabaseUser(sbUser: any, profile?: UserProfile | null): User {
    const role = (sbUser.user_metadata?.role as 'farmer' | 'admin') || (profile?.email?.includes('admin') ? 'admin' : 'farmer');
    return {
      id: sbUser.id,
      email: sbUser.email || '',
      role: role,
      is_active: true,
      created_at: sbUser.created_at,
      profile: profile || {
        id: sbUser.id,
        email: sbUser.email || '',
        full_name: sbUser.user_metadata?.full_name || sbUser.email?.split('@')[0] || 'Farmer',
        preferred_language: sbUser.user_metadata?.preferred_language || 'en',
      },
    };
  },

  /**
   * Fetch profile row from public.profiles table
   */
  async getProfile(userId: string): Promise<UserProfile | null> {
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .maybeSingle();

      if (error) {
        console.warn('Could not load profile from Supabase:', error.message);
        return null;
      }
      return data as UserProfile;
    } catch (e) {
      console.warn('Error querying profile table:', e);
      return null;
    }
  },

  /**
   * Update or upsert user profile
   */
  async updateProfile(userId: string, updates: Partial<UserProfile>): Promise<UserProfile | null> {
    const payload = {
      id: userId,
      ...updates,
      updated_at: new Date().toISOString(),
    };

    const { data, error } = await supabase
      .from('profiles')
      .upsert(payload)
      .select()
      .single();

    if (error) {
      throw new Error(error.message);
    }
    return data as UserProfile;
  },

  /**
   * Supabase Auth Sign Up
   */
  async signup(data: SignupRequest): Promise<AuthResponse> {
    const { data: authData, error } = await supabase.auth.signUp({
      email: data.email.trim().toLowerCase(),
      password: data.password,
      options: {
        data: {
          full_name: data.full_name || data.email.split('@')[0],
          preferred_language: 'en',
          role: 'farmer',
        },
      },
    });

    if (error) {
      throw new Error(error.message);
    }

    if (!authData.user) {
      throw new Error('Sign up failed: no user returned');
    }

    const token = authData.session?.access_token || '';
    if (token) {
      this.setToken(token);
    }

    const profile = await this.getProfile(authData.user.id);
    const user = this.mapSupabaseUser(authData.user, profile);

    return {
      message: authData.session ? 'Account created successfully.' : 'Account created. Please verify your email if required.',
      user,
      access_token: token,
      token_type: 'bearer',
    };
  },

  /**
   * Supabase Auth Log In
   */
  async login(data: LoginRequest): Promise<AuthResponse> {
    const { data: authData, error } = await supabase.auth.signInWithPassword({
      email: data.email.trim().toLowerCase(),
      password: data.password,
    });

    if (error) {
      throw new Error(error.message);
    }

    if (!authData.user || !authData.session) {
      throw new Error('Login failed: invalid credentials or unconfirmed email');
    }

    const token = authData.session.access_token;
    this.setToken(token);

    const profile = await this.getProfile(authData.user.id);
    const user = this.mapSupabaseUser(authData.user, profile);

    return {
      message: 'Login successful.',
      user,
      access_token: token,
      token_type: 'bearer',
    };
  },

  /**
   * Get Current Logged-in User
   */
  async getCurrentUser(): Promise<User | null> {
    const { data: { user: sbUser }, error } = await supabase.auth.getUser();
    if (error || !sbUser) {
      this.removeToken();
      return null;
    }

    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      this.setToken(session.access_token);
    }

    const profile = await this.getProfile(sbUser.id);
    return this.mapSupabaseUser(sbUser, profile);
  },

  /**
   * Send Password Reset Email
   */
  async resetPassword(email: string): Promise<void> {
    const { error } = await supabase.auth.resetPasswordForEmail(email.trim().toLowerCase(), {
      redirectTo: window.location.origin,
    });
    if (error) {
      throw new Error(error.message);
    }
  },

  /**
   * Supabase Auth Log Out
   */
  async logout(): Promise<void> {
    try {
      await supabase.auth.signOut();
    } catch (err) {
      console.warn('Supabase signOut error:', err);
    } finally {
      this.removeToken();
    }
  },
};

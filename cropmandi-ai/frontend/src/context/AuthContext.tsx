import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { ReactNode } from 'react';
import type { User, UserProfile, LoginRequest, SignupRequest } from '../types/auth';
import { authService } from '../services/authService';
import { supabase } from '../lib/supabase';

interface AuthContextType {
  user: User | null;
  profile: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  signup: (data: SignupRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  updateProfile: (updates: Partial<UserProfile>) => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(authService.getToken());
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const refreshUser = useCallback(async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      if (currentUser) {
        setUser(currentUser);
        setProfile(currentUser.profile || null);
        setToken(authService.getToken());
      } else {
        setUser(null);
        setProfile(null);
        setToken(null);
      }
    } catch (err) {
      console.warn('Failed to refresh user:', err);
      setUser(null);
      setProfile(null);
      setToken(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // Initial fetch
    refreshUser();

    // Supabase auth state change listener
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (session?.user) {
        if (session.access_token) {
          authService.setToken(session.access_token);
          setToken(session.access_token);
        }
        const profileData = await authService.getProfile(session.user.id);
        const mappedUser = authService.mapSupabaseUser(session.user, profileData);
        setUser(mappedUser);
        setProfile(profileData);
      } else if (event === 'SIGNED_OUT') {
        authService.removeToken();
        setUser(null);
        setProfile(null);
        setToken(null);
      }
      setIsLoading(false);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [refreshUser]);

  const login = async (data: LoginRequest) => {
    setIsLoading(true);
    try {
      const res = await authService.login(data);
      setUser(res.user);
      setProfile(res.user.profile || null);
      setToken(res.access_token);
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (data: SignupRequest) => {
    setIsLoading(true);
    try {
      const res = await authService.signup(data);
      setUser(res.user);
      setProfile(res.user.profile || null);
      setToken(res.access_token);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await authService.logout();
    } finally {
      setUser(null);
      setProfile(null);
      setToken(null);
      setIsLoading(false);
    }
  };

  const updateProfile = async (updates: Partial<UserProfile>) => {
    if (!user) return;
    const updated = await authService.updateProfile(user.id, updates);
    if (updated) {
      setProfile(updated);
      setUser((prev) => (prev ? { ...prev, profile: updated } : null));
    }
  };

  const resetPassword = async (email: string) => {
    await authService.resetPassword(email);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        token,
        isAuthenticated: !!user,
        isLoading,
        login,
        signup,
        logout,
        refreshUser,
        updateProfile,
        resetPassword,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

interface Doctor {
  id: number;
  full_name: string;
  email: string;
  specialty: string | null;
  is_active: boolean;
}

interface AuthContextType {
  doctor: Doctor | null;
  token: string | null;
  login: (token: string, doctor: Doctor) => void;
  logout: () => void;
  isAuthenticated: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [doctor, setDoctor] = useState<Doctor | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      fetchDoctor(storedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchDoctor = async (currentToken: string) => {
    try {
      const response = await fetch('/api/v1/auth/me', {
        headers: {
          Authorization: `Bearer ${currentToken}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setDoctor(data);
      } else {
        logout();
      }
    } catch (error) {
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = (newToken: string, doctorData: Doctor) => {
    setToken(newToken);
    setDoctor(doctorData);
    localStorage.setItem('token', newToken);
  };

  const logout = () => {
    setToken(null);
    setDoctor(null);
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider
      value={{
        doctor,
        token,
        login,
        logout,
        isAuthenticated: !!token,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

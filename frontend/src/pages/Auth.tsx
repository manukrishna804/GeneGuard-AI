import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';

export default function Auth() {
  const { login, isAuthenticated } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [specialty, setSpecialty] = useState('');
  
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);

        const res = await fetch('/api/v1/auth/login', {
          method: 'POST',
          body: formData,
        });

        const contentType = res.headers.get('content-type');
        if (!res.ok) {
          if (contentType && contentType.includes('application/json')) {
            const data = await res.json();
            throw new Error(data.detail || 'Login failed');
          } else {
            throw new Error(`Server error: ${res.statusText}. The backend might be starting up.`);
          }
        }

        const data = await res.json();
        login(data.access_token, data.doctor);
      } else {
        const res = await fetch('/api/v1/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email,
            password,
            full_name: fullName,
            specialty: specialty || null,
          }),
        });

        if (!res.ok) {
          const contentType = res.headers.get('content-type');
          if (contentType && contentType.includes('application/json')) {
            const data = await res.json();
            throw new Error(data.detail || 'Registration failed');
          } else {
             throw new Error(`Server error: ${res.statusText}. The backend might be starting up.`);
          }
        }

        // Auto login after register
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);

        const loginRes = await fetch('/api/v1/auth/login', {
          method: 'POST',
          body: formData,
        });

        if (loginRes.ok) {
          const data = await loginRes.json();
          login(data.access_token, data.doctor);
        } else {
          setIsLogin(true); // fall back to login screen if auto-login fails
        }
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-lg border border-gray-100 p-8">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <span className="material-symbols-outlined text-4xl text-primary">genetics</span>
            <span className="text-3xl font-bold text-gray-900 tracking-tight">GeneGuard AI</span>
          </div>
          <h2 className="text-xl font-semibold text-gray-700">
            {isLogin ? 'Doctor Login' : 'Create Doctor Account'}
          </h2>
          <p className="text-sm text-gray-500 mt-2">
            Secure access for clinical professionals
          </p>
        </div>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm flex items-start gap-2">
            <span className="material-symbols-outlined text-sm mt-0.5 text-red-500">error</span>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input
                type="text"
                required
                className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none text-gray-900"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Dr. Jane Smith"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
            <input
              type="email"
              required
              className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none text-gray-900"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="doctor@hospital.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              required
              minLength={6}
              className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none text-gray-900"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>

          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Specialty (Optional)</label>
              <input
                type="text"
                className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none text-gray-900"
                value={specialty}
                onChange={(e) => setSpecialty(e.target.value)}
                placeholder="Medical Genetics"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary hover:bg-[#005049] text-white font-semibold py-2.5 rounded-lg transition-colors flex justify-center items-center gap-2 mt-6 disabled:opacity-70"
          >
            {loading ? (
              <span className="material-symbols-outlined animate-spin text-sm">autorenew</span>
            ) : (
              <span className="material-symbols-outlined text-sm">{isLogin ? 'login' : 'person_add'}</span>
            )}
            {isLogin ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-600 border-t border-gray-100 pt-6">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button
            type="button"
            onClick={() => {
              setIsLogin(!isLogin);
              setError('');
            }}
            className="text-primary hover:underline font-semibold"
          >
            {isLogin ? 'Register here' : 'Sign in'}
          </button>
        </div>
      </div>
    </div>
  );
}

import { useEffect, useState } from 'react';
import ResumeForm from './components/ResumeForm';
import AdminLogin from './components/AdminLogin';
import AdminDashboard from './components/AdminDashboard';

function App() {
  const [view, setView] = useState<'form' | 'admin'>('form');
  const [sessionToken, setSessionToken] = useState<string | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem('admin_session_token');
    if (saved) {
      setSessionToken(saved);
    }
  }, []);

  const handleLoginSuccess = (token: string) => {
    setSessionToken(token);
    localStorage.setItem('admin_session_token', token);
  };

  const handleLogout = () => {
    setSessionToken(null);
    localStorage.removeItem('admin_session_token');
    setView('form');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-xl font-bold text-gray-900">Resume Builder</h1>
            <div className="flex gap-4">
              {!sessionToken && (
                <>
                  <button
                    onClick={() => setView('form')}
                    className={`px-4 py-2 rounded-lg transition-colors ${
                      view === 'form'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    Create Resume
                  </button>
                  <button
                    onClick={() => setView('admin')}
                    className={`px-4 py-2 rounded-lg transition-colors ${
                      view === 'admin'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    Admin
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {sessionToken ? (
        <AdminDashboard sessionToken={sessionToken} onLogout={handleLogout} />
      ) : view === 'form' ? (
        <ResumeForm />
      ) : (
        <AdminLogin onLoginSuccess={handleLoginSuccess} />
      )}
    </div>
  );
}

export default App;

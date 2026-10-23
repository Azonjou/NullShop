import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import AuthPage from './pages/AuthPage';
import useAuthStore from './store/useAuthStore';
import StarRating from './components/StarRating';

// Временная заглушка для главной страницы

function TempHome() {
  const { user, isAuthenticated, logout } = useAuthStore();
  
  return (
    
    <div className="max-w-4xl mx-auto p-8 text-center">
      <h1 className="text-3xl font-bold text-slate-900 mb-4">
        Главная страница NullShop
      </h1>
      {isAuthenticated && user ? (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6 inline-block">
          <p className="text-emerald-800 font-medium">
            Вы вошли как: <span className="font-bold">{user.email}</span>
          </p>
          <p className="text-emerald-600 text-sm mt-1">
            Ваша роль: <span className="uppercase font-semibold">{user.role}</span>
          </p>
          <button
            onClick={logout}
            className="mt-4 px-4 py-2 bg-rose-600 text-white text-sm rounded-lg hover:bg-rose-700 cursor-pointer"
          >
            Выйти из аккаунта
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <p className="text-slate-600">Вы пока не авторизованы.</p>
          <Link
            to="/auth"
            className="inline-block px-6 py-2.5 bg-indigo-600 text-white font-medium rounded-xl hover:bg-indigo-700"
          >
            Перейти ко входу / регистрации
          </Link>
        </div>
      )}
    </div>
  );
}

export default function App() {
  const { fetchMe } = useAuthStore();

  useEffect(() => {
    fetchMe();
  }, [fetchMe]);

  return (
    <BrowserRouter>
      <Toaster position="top-right" />

      <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold text-indigo-600">
          NullShop
        </Link>
        <nav className="flex gap-4 text-sm font-medium">
          <Link to="/" className="text-slate-600 hover:text-indigo-600">
            Каталог
          </Link>
          <Link to="/auth" className="text-slate-600 hover:text-indigo-600">
            Вход / Регистрация
          </Link>
        </nav>
      </header>

      <Routes>
        <Route path="/" element={<TempHome />} />
        <Route path="/auth" element={<AuthPage />} />
      </Routes>
    </BrowserRouter>
  );
}
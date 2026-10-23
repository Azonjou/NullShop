import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { LogIn, UserPlus, Mail, Lock, ShieldCheck } from 'lucide-react';
import useAuthStore from '../store/useAuthStore';

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('buyer');

  const { login, register, isLoading } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (password.length < 8) {
      toast.error('Пароль должен содержать минимум 8 символов');
      return;
    }

    if (isLogin) {
      const res = await login(email, password);
      if (res.success) {
        toast.success('С возвращением!');
        navigate('/');
      } else {
        toast.error(res.message);
      }
    } else {
      const res = await register(email, password, role);
      if (res.success) {
        toast.success('Аккаунт успешно создан!');
        navigate('/');
      } else {
        toast.error(res.message);
      }
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-slate-50 px-4 py-12">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg border border-slate-100 p-8">
        {/* Заголовок */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-slate-900">
            {isLogin ? 'Вход в NullShop' : 'Создание аккаунта'}
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            {isLogin
              ? 'Введите свои данные для доступа к магазину'
              : 'Зарегистрируйтесь как покупатель, продавец или админ'}
          </p>
        </div>

        {/* Переключатель Вход / Регистрация */}
        <div className="grid grid-cols-2 bg-slate-100 p-1 rounded-xl mb-6">
          <button
            type="button"
            onClick={() => setIsLogin(true)}
            className={`flex items-center justify-center gap-2 py-2 text-sm font-medium rounded-lg transition-all cursor-pointer ${
              isLogin
                ? 'bg-white text-indigo-600 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <LogIn className="w-4 h-4" />
            Вход
          </button>
          <button
            type="button"
            onClick={() => setIsLogin(false)}
            className={`flex items-center justify-center gap-2 py-2 text-sm font-medium rounded-lg transition-all cursor-pointer ${
              !isLogin
                ? 'bg-white text-indigo-600 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <UserPlus className="w-4 h-4" />
            Регистрация
          </button>
        </div>

        {/* Форма */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Email
            </label>
            <div className="relative">
              <Mail className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Пароль (от 8 символов)
            </label>
            <div className="relative">
              <Lock className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
              />
            </div>
          </div>

          {/* Выбор роли при регистрации */}
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                Тип аккаунта
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setRole('buyer')}
                  className={`py-2.5 px-3 rounded-xl border text-sm font-medium transition-all cursor-pointer ${
                    role === 'buyer'
                      ? 'border-indigo-600 bg-indigo-50 text-indigo-700'
                      : 'border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  Покупатель
                </button>
                <button
                  type="button"
                  onClick={() => setRole('seller')}
                  className={`py-2.5 px-3 rounded-xl border text-sm font-medium transition-all cursor-pointer ${
                    role === 'seller'
                      ? 'border-indigo-600 bg-indigo-50 text-indigo-700'
                      : 'border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  Продавец
                </button>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-medium rounded-xl shadow-sm transition-colors cursor-pointer mt-2"
          >
            {isLoading
              ? 'Загрузка...'
              : isLogin
              ? 'Войти в аккаунт'
              : 'Зарегистрироваться'}
          </button>
        </form> ы {/*Посхалко*/}
      </div>
    </div>
  );
}
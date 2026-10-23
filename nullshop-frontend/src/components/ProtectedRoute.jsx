import { Navigate } from 'react-router-dom';
import useAuthStore from '../store/useAuthStore';

export default function ProtectedRoute({ children, allowedRoles }) {
    
    const { isAuthenticated, user, isLoading } = useAuthStore((state) => ({
        isAuthenticated: state.isAuthenticated,
        user: state.user,
        isLoading: state.isLoading,
    }));

    if (isLoading) { return <div className="p-8 text-center">Загрузка...</div> }
    if (!isAuthenticated) { return <Navigate to="/auth" replace/> }
    if (allowedRoles && !allowedRoles.includes(user?.role)) { return <Navigate to="/" replace/> }

    return children;

}
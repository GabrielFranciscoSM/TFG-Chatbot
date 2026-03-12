import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";

/**
 * PublicRoute - Wrapper for public pages (login, register)
 * Redirects authenticated users to their role-appropriate page
 */
export default function PublicRoute() {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (isAuthenticated && user) {
    // Redirect based on role
    if (user.role === "admin") {
      return <Navigate to="/admin" replace />;
    }
    if (user.role === "professor") {
      const hasSubjects = user.subjects && user.subjects.length > 0;
      return <Navigate to={hasSubjects ? "/dashboard" : "/settings"} replace />;
    }
    // Students go to chat
    return <Navigate to="/chat" replace />;
  }

  return <Outlet />;
}

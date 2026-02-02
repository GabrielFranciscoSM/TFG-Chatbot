import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";

/**
 * Route guard that only allows students to access chat.
 * Redirects professors and admins to /dashboard or /admin.
 */
export default function RequireStudent() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Only students can access chat
  if (user.role === "student") {
    return <Outlet />;
  }

  // Redirect professors/admins to appropriate page
  if (user.role === "admin") {
    return <Navigate to="/admin" replace />;
  }

  // Professors go to dashboard if they have subjects, otherwise settings
  const hasSubjects = user.subjects && user.subjects.length > 0;
  if (hasSubjects) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Navigate to="/settings" replace />;
}

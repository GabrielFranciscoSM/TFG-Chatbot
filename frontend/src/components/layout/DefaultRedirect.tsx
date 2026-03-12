import { Navigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";

/**
 * Smart redirect component that sends users to the appropriate page based on their role.
 * - Students → /chat
 * - Professors with subjects → /dashboard
 * - Professors without subjects → /settings
 * - Admins → /admin
 */
export default function DefaultRedirect() {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Not authenticated - go to login
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  // Route based on role
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

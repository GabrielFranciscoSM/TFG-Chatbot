import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";

/**
 * Route guard that allows users with subjects (professors, or admins with subjects).
 * Redirects users without subjects to /chat.
 */
export default function RequireProfessor() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Allow professors, or admins who have subjects assigned
  const hasSubjects = user?.subjects && user.subjects.length > 0;
  const canManageClasses = user?.role === "professor" || (user?.role === "admin" && hasSubjects);

  if (!user || !canManageClasses) {
    return <Navigate to="/chat" replace />;
  }

  return <Outlet />;
}

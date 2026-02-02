import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import AppLayout from "@/components/layout/AppLayout";
import DefaultRedirect from "@/components/layout/DefaultRedirect";
import PublicRoute from "@/components/layout/PublicRoute";
import RequireAdmin from "@/components/layout/RequireAdmin";
import RequireAuth from "@/components/layout/RequireAuth";
import RequireProfessor from "@/components/layout/RequireProfessor";
import RequireStudent from "@/components/layout/RequireStudent";
import { Toaster } from "@/components/ui/sonner";
import { AuthProvider } from "@/context/AuthContext";
import AdminDashboard from "@/pages/admin/AdminDashboard";
import LoginPage from "@/pages/auth/LoginPage";
import RegisterPage from "@/pages/auth/RegisterPage";
import ChatPage from "@/pages/chat/ChatPage";
import DashboardPage from "@/pages/dashboard/DashboardPage";
import SettingsPage from "@/pages/settings/SettingsPage";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Routes - Redirect to /chat if already logged in */}
            <Route element={<PublicRoute />}>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
            </Route>

            {/* Protected Routes */}
            <Route element={<RequireAuth />}>
              <Route element={<AppLayout />}>
                {/* Student-only routes */}
                <Route element={<RequireStudent />}>
                  <Route path="/chat" element={<ChatPage />} />
                </Route>

                <Route path="/settings" element={<SettingsPage />} />

                {/* Professor and Admin routes */}
                <Route element={<RequireProfessor />}>
                  <Route path="/dashboard" element={<DashboardPage />} />
                </Route>

                {/* Admin-only routes */}
                <Route element={<RequireAdmin />}>
                  <Route path="/admin" element={<AdminDashboard />} />
                </Route>
              </Route>
            </Route>

            {/* Default Redirect - Role-based */}
            <Route path="*" element={<DefaultRedirect />} />
          </Routes>
          <Toaster />
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;

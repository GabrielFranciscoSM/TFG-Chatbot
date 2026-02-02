import { BookOpen, GraduationCap, MessageSquare, Plus, Shield, UserCog, Users } from "lucide-react";
import { useState } from "react";
import { AssignSubjectDialog } from "@/components/admin/AssignSubjectDialog";
import { CreateSubjectDialog } from "@/components/admin/CreateSubjectDialog";
import { PromoteUserDialog } from "@/components/admin/PromoteUserDialog";
import { SubjectsTable } from "@/components/admin/SubjectsTable";
import { UsersTable } from "@/components/admin/UsersTable";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAdminStats, useUsers } from "@/hooks/useAdmin";
import type { UserInfo } from "@/types/admin";

export default function AdminDashboard() {
  const { data: stats, isLoading: statsLoading } = useAdminStats();
  const { data: users, isLoading: usersLoading } = useUsers();

  const [assignDialogOpen, setAssignDialogOpen] = useState(false);
  const [promoteDialogOpen, setPromoteDialogOpen] = useState(false);
  const [createSubjectDialogOpen, setCreateSubjectDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UserInfo | undefined>();

  const handleAssignSubject = (userInfo: UserInfo) => {
    setSelectedUser(userInfo);
    setAssignDialogOpen(true);
  };

  const handlePromoteUser = (userInfo: UserInfo) => {
    setSelectedUser(userInfo);
    setPromoteDialogOpen(true);
  };

  return (
    <div className="p-4 md:p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Panel de Administración</h1>
          <p className="text-muted-foreground">
            Gestiona usuarios y visualiza estadísticas del sistema
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            size="sm"
            className="flex-1 sm:flex-none"
            onClick={() => setCreateSubjectDialogOpen(true)}
          >
            <Plus className="mr-2 h-4 w-4" />
            <span className="sm:inline">Crear Asignatura</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="flex-1 sm:flex-none"
            onClick={() => {
              setSelectedUser(undefined);
              setAssignDialogOpen(true);
            }}
          >
            <GraduationCap className="mr-2 h-4 w-4" />
            <span className="sm:inline">Asignar Asignatura</span>
          </Button>
          <Button
            size="sm"
            className="flex-1 sm:flex-none"
            onClick={() => {
              setSelectedUser(undefined);
              setPromoteDialogOpen(true);
            }}
          >
            <UserCog className="mr-2 h-4 w-4" />
            <span className="sm:inline">Cambiar Rol</span>
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Estudiantes</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {statsLoading ? "..." : (stats?.total_students ?? 0)}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Profesores</CardTitle>
            <GraduationCap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {statsLoading ? "..." : (stats?.total_professors ?? 0)}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Admins</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {statsLoading ? "..." : (stats?.total_admins ?? 0)}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Sesiones</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {statsLoading ? "..." : (stats?.total_sessions ?? 0)}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Asignaturas</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {statsLoading ? "..." : (stats?.total_subjects ?? 0)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Activity Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Actividad - Últimos 7 días</CardTitle>
          <CardDescription>Sesiones creadas por día</CardDescription>
        </CardHeader>
        <CardContent>
          {statsLoading ? (
            <div className="h-32 flex items-center justify-center">
              <p className="text-muted-foreground">Cargando...</p>
            </div>
          ) : (
            <div className="flex items-end gap-2 h-32">
              {stats?.sessions_last_7_days.map((day) => {
                const maxCount = Math.max(
                  ...(stats?.sessions_last_7_days.map((d) => d.count) || [1]),
                  1,
                );
                const height = (day.count / maxCount) * 100;
                return (
                  <div key={day.date} className="flex-1 flex flex-col items-center gap-1">
                    <div
                      className="w-full bg-primary rounded-t"
                      style={{ height: `${Math.max(height, 4)}%` }}
                    />
                    <span className="text-xs text-muted-foreground">
                      {new Date(day.date).toLocaleDateString("es", { weekday: "short" })}
                    </span>
                    <span className="text-xs font-medium">{day.count}</span>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Tabs for Users and Subjects */}
      <Tabs defaultValue="users" className="space-y-4">
        <TabsList>
          <TabsTrigger value="users" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            Usuarios
          </TabsTrigger>
          <TabsTrigger value="subjects" className="flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            Asignaturas
          </TabsTrigger>
        </TabsList>
        <TabsContent value="users">
          <Card>
            <CardHeader>
              <CardTitle>Usuarios del Sistema</CardTitle>
              <CardDescription>Gestiona los roles y asignaturas de los usuarios</CardDescription>
            </CardHeader>
            <CardContent>
              <UsersTable
                users={users ?? []}
                isLoading={usersLoading}
                onAssignSubject={handleAssignSubject}
                onPromoteUser={handlePromoteUser}
              />
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="subjects">
          <Card>
            <CardHeader>
              <CardTitle>Asignaturas</CardTitle>
              <CardDescription>Gestiona las asignaturas del sistema</CardDescription>
            </CardHeader>
            <CardContent>
              <SubjectsTable />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Dialogs */}
      <CreateSubjectDialog
        open={createSubjectDialogOpen}
        onOpenChange={setCreateSubjectDialogOpen}
      />
      <AssignSubjectDialog
        open={assignDialogOpen}
        onOpenChange={setAssignDialogOpen}
        professorUsername={selectedUser?.role === "professor" ? selectedUser.username : undefined}
      />
      <PromoteUserDialog
        open={promoteDialogOpen}
        onOpenChange={setPromoteDialogOpen}
        user={selectedUser}
      />
    </div>
  );
}

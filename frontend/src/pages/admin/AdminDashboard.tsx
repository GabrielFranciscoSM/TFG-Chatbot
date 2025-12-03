import {
  BookOpen,
  GraduationCap,
  MessageSquare,
  MoreVertical,
  Shield,
  UserCog,
  Users,
} from "lucide-react";
import { useState } from "react";
import { AssignSubjectDialog } from "@/components/admin/AssignSubjectDialog";
import { PromoteUserDialog } from "@/components/admin/PromoteUserDialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAdminStats, useUsers } from "@/hooks/useAdmin";
import type { UserInfo } from "@/types/admin";

export default function AdminDashboard() {
  const { data: stats, isLoading: statsLoading } = useAdminStats();
  const { data: users, isLoading: usersLoading } = useUsers();

  const [assignDialogOpen, setAssignDialogOpen] = useState(false);
  const [promoteDialogOpen, setPromoteDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UserInfo | undefined>();

  const handleAssignSubject = (userInfo: UserInfo) => {
    setSelectedUser(userInfo);
    setAssignDialogOpen(true);
  };

  const handlePromoteUser = (userInfo: UserInfo) => {
    setSelectedUser(userInfo);
    setPromoteDialogOpen(true);
  };

  const roleLabels = {
    student: "Estudiante",
    professor: "Profesor",
    admin: "Admin",
  };

  const roleBadgeVariant = {
    student: "secondary" as const,
    professor: "default" as const,
    admin: "destructive" as const,
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Panel de Administración</h1>
          <p className="text-muted-foreground">
            Gestiona usuarios y visualiza estadísticas del sistema
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => {
              setSelectedUser(undefined);
              setAssignDialogOpen(true);
            }}
          >
            <GraduationCap className="mr-2 h-4 w-4" />
            Asignar Asignatura
          </Button>
          <Button
            onClick={() => {
              setSelectedUser(undefined);
              setPromoteDialogOpen(true);
            }}
          >
            <UserCog className="mr-2 h-4 w-4" />
            Cambiar Rol
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

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>Usuarios del Sistema</CardTitle>
          <CardDescription>Gestiona los roles y asignaturas de los usuarios</CardDescription>
        </CardHeader>
        <CardContent>
          {usersLoading ? (
            <p className="text-muted-foreground">Cargando usuarios...</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Usuario</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Rol</TableHead>
                  <TableHead>Asignaturas</TableHead>
                  <TableHead className="w-[50px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users?.map((u) => (
                  <TableRow key={u.username}>
                    <TableCell className="font-medium">{u.username}</TableCell>
                    <TableCell>{u.email}</TableCell>
                    <TableCell>
                      <Badge variant={roleBadgeVariant[u.role]}>{roleLabels[u.role]}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {u.subjects.length > 0 ? (
                          u.subjects.map((s) => (
                            <Badge key={s} variant="outline" className="text-xs">
                              {s}
                            </Badge>
                          ))
                        ) : (
                          <span className="text-muted-foreground text-sm">—</span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handlePromoteUser(u)}>
                            <UserCog className="mr-2 h-4 w-4" />
                            Cambiar rol
                          </DropdownMenuItem>
                          {u.role === "professor" && (
                            <DropdownMenuItem onClick={() => handleAssignSubject(u)}>
                              <GraduationCap className="mr-2 h-4 w-4" />
                              Asignar asignatura
                            </DropdownMenuItem>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Dialogs */}
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

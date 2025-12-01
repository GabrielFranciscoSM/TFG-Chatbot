import { useAuth } from "@/context/AuthContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, MessageSquare, BookOpen, TrendingUp } from "lucide-react";

export default function AdminDashboard() {
  const { user } = useAuth();

  // Placeholder stats - will be fetched from API in Week 3
  const stats = [
    { title: "Estudiantes", value: "—", icon: Users },
    { title: "Sesiones", value: "—", icon: MessageSquare },
    { title: "Documentos", value: "—", icon: BookOpen },
    { title: "Consultas hoy", value: "—", icon: TrendingUp },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Bienvenido, {user?.email}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Placeholder for charts */}
      <Card>
        <CardHeader>
          <CardTitle>Actividad Reciente</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center text-muted-foreground border-2 border-dashed rounded-lg">
            <p>Los gráficos de actividad se implementarán en la Semana 3</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

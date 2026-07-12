import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, Package, Server } from "lucide-react";
import { api } from "../api/client";
import { Card, PageHeader } from "../components/Layout";
import { DashboardStats } from "../types/models";

export function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    api.get<DashboardStats>("/dashboard/stats").then(setStats);
  }, []);

  const cards = [
    { label: "Assets", value: stats?.assets ?? 0, icon: Server },
    { label: "Software", value: stats?.software_packages ?? 0, icon: Package },
    { label: "Open Vulns", value: stats?.open_vulnerabilities ?? 0, icon: AlertTriangle },
    { label: "Tasks", value: stats?.remediation_tasks ?? 0, icon: CheckCircle2 }
  ];

  return (
    <>
      <PageHeader title="Dashboard" />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <Card key={card.label}>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-slate-500">{card.label}</div>
                  <div className="mt-1 text-3xl font-semibold">{card.value}</div>
                </div>
                <Icon className="text-signal" size={24} />
              </div>
            </Card>
          );
        })}
      </div>
      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <Card>
          <h2 className="mb-3 text-sm font-semibold uppercase text-slate-500">Risk posture</h2>
          <div className="text-4xl font-semibold">{stats?.average_risk_score ?? 0}</div>
          <div className="mt-2 text-sm text-slate-500">Average open vulnerability risk score</div>
        </Card>
        <Card>
          <h2 className="mb-3 text-sm font-semibold uppercase text-slate-500">Severity counts</h2>
          <div className="space-y-2">
            {Object.entries(stats?.severity_counts ?? {}).map(([severity, count]) => (
              <div key={severity} className="flex items-center justify-between border-b border-line pb-2 text-sm">
                <span className="font-medium">{severity}</span>
                <span>{count}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </>
  );
}
// Project version: VulnScope V1.5


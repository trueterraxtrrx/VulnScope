import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";
import { api } from "../api/client";
import { DataTable } from "../components/DataTable";
import { PageHeader } from "../components/Layout";
import { Vulnerability } from "../types/models";

export function VulnerabilitiesPage() {
  const [rows, setRows] = useState<Vulnerability[]>([]);

  async function load() {
    setRows(await api.get<Vulnerability[]>("/vulnerabilities"));
  }

  useEffect(() => {
    load();
  }, []);

  async function match() {
    await api.post("/vulnerabilities/match", {});
    await load();
  }

  async function updateStatus(id: string, status: string) {
    await api.patch(`/vulnerabilities/${id}/status`, { status });
    await load();
  }

  return (
    <>
      <PageHeader
        title="Vulnerabilities"
        actions={<button onClick={match} className="focus-ring inline-flex items-center gap-2 bg-ink px-4 py-2 text-white"><RefreshCw size={16} /> Match</button>}
      />
      <DataTable
        rows={rows}
        columns={[
          { key: "asset", header: "Asset", render: (row) => row.asset_id.slice(0, 8) },
          { key: "cve", header: "CVE", render: (row) => row.cve_id.slice(0, 8) },
          { key: "risk", header: "Risk", render: (row) => <span className="font-semibold">{row.risk_score}</span> },
          { key: "status", header: "Status", render: (row) => row.status },
          {
            key: "action",
            header: "Action",
            render: (row) => (
              <select className="focus-ring border border-line px-2 py-1" value={row.status} onChange={(e) => updateStatus(row.id, e.target.value)}>
                <option value="open">open</option>
                <option value="fixed">fixed</option>
                <option value="accepted">accepted</option>
                <option value="false_positive">false_positive</option>
              </select>
            )
          }
        ]}
      />
    </>
  );
}
// Project version: VulnScope V1.5







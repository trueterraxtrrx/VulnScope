import { FormEvent, useEffect, useState } from "react";
import { api } from "../api/client";
import { DataTable } from "../components/DataTable";
import { Card, PageHeader } from "../components/Layout";

type Me = {
  email: string;
  full_name?: string | null;
  role: string;
  organization: { id: string; name: string };
};

type AuditLog = {
  id: string;
  action: string;
  target_type?: string | null;
  target_id?: string | null;
  metadata_json: Record<string, unknown>;
  created_at: string;
};

type APIKey = {
  id: string;
  name: string;
  key_prefix: string;
  created_at: string;
  last_used_at?: string | null;
};

export function SettingsPage() {
  const [me, setMe] = useState<Me | null>(null);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [keys, setKeys] = useState<APIKey[]>([]);
  const [keyName, setKeyName] = useState("import-pipeline");
  const [createdToken, setCreatedToken] = useState("");

  useEffect(() => {
    api.get<Me>("/me").then(setMe);
    api.get<AuditLog[]>("/audit-logs").then(setLogs);
    api.get<APIKey[]>("/api-keys").then(setKeys);
  }, []);

  async function createKey(event: FormEvent) {
    event.preventDefault();
    const created = await api.post<APIKey & { token: string }>("/api-keys", { name: keyName });
    setCreatedToken(created.token);
    setKeys(await api.get<APIKey[]>("/api-keys"));
  }

  return (
    <>
      <PageHeader title="Settings" />
      <Card className="mb-4">
        <div className="grid gap-4 sm:grid-cols-3">
          <div>
            <div className="text-xs uppercase text-slate-500">Organization</div>
            <div className="mt-1 font-semibold">{me?.organization.name || "-"}</div>
          </div>
          <div>
            <div className="text-xs uppercase text-slate-500">User</div>
            <div className="mt-1 font-semibold">{me?.email || "-"}</div>
          </div>
          <div>
            <div className="text-xs uppercase text-slate-500">Role</div>
            <div className="mt-1 font-semibold">{me?.role || "-"}</div>
          </div>
        </div>
      </Card>
      <Card className="mb-4">
        <h2 className="mb-3 text-lg font-semibold">API keys</h2>
        <form className="mb-3 flex flex-col gap-3 sm:flex-row" onSubmit={createKey}>
          <input className="focus-ring flex-1 border border-line px-3 py-2" value={keyName} onChange={(e) => setKeyName(e.target.value)} />
          <button className="focus-ring bg-ink px-4 py-2 text-white">Create key</button>
        </form>
        {createdToken && <div className="mb-3 border border-warn/30 bg-amber-50 p-3 font-mono text-xs text-warn">{createdToken}</div>}
        <DataTable
          rows={keys}
          columns={[
            { key: "name", header: "Name", render: (row) => row.name },
            { key: "prefix", header: "Prefix", render: (row) => row.key_prefix },
            { key: "created", header: "Created", render: (row) => new Date(row.created_at).toLocaleString() }
          ]}
        />
      </Card>
      <h2 className="mb-3 text-lg font-semibold">Audit logs</h2>
      <DataTable
        rows={logs}
        columns={[
          { key: "time", header: "Time", render: (row) => new Date(row.created_at).toLocaleString() },
          { key: "action", header: "Action", render: (row) => row.action },
          { key: "target", header: "Target", render: (row) => [row.target_type, row.target_id?.slice(0, 8)].filter(Boolean).join(":") || "-" }
        ]}
      />
    </>
  );
}
// Project version: VulnScope V1.5








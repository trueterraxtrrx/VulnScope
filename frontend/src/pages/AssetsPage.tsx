import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Plus } from "lucide-react";
import { api } from "../api/client";
import { DataTable } from "../components/DataTable";
import { Card, PageHeader } from "../components/Layout";
import { Asset } from "../types/models";

export function AssetsPage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [hostname, setHostname] = useState("");
  const [environment, setEnvironment] = useState("production");
  const [criticality, setCriticality] = useState(3);

  async function load() {
    setAssets(await api.get<Asset[]>("/assets"));
  }

  useEffect(() => {
    load();
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    await api.post<Asset>("/assets", { hostname, environment, criticality });
    setHostname("");
    await load();
  }

  return (
    <>
      <PageHeader title="Assets" />
      <Card className="mb-4">
        <form className="grid gap-3 md:grid-cols-[1fr_180px_140px_auto]" onSubmit={submit}>
          <input className="focus-ring border border-line px-3 py-2" value={hostname} onChange={(e) => setHostname(e.target.value)} placeholder="hostname" required />
          <select className="focus-ring border border-line px-3 py-2" value={environment} onChange={(e) => setEnvironment(e.target.value)}>
            <option value="production">production</option>
            <option value="internet">internet</option>
            <option value="staging">staging</option>
            <option value="internal">internal</option>
          </select>
          <input className="focus-ring border border-line px-3 py-2" type="number" min={1} max={5} value={criticality} onChange={(e) => setCriticality(Number(e.target.value))} />
          <button className="focus-ring inline-flex items-center justify-center gap-2 bg-ink px-4 py-2 text-white"><Plus size={16} /> Add</button>
        </form>
      </Card>
      <DataTable
        rows={assets}
        columns={[
          { key: "host", header: "Hostname", render: (row) => <Link className="font-semibold text-signal" to={`/assets/${row.id}`}>{row.hostname}</Link> },
          { key: "ip", header: "IP", render: (row) => row.ip_address || "-" },
          { key: "os", header: "OS", render: (row) => [row.os_name, row.os_version].filter(Boolean).join(" ") || "-" },
          { key: "env", header: "Environment", render: (row) => row.environment },
          { key: "crit", header: "Criticality", render: (row) => row.criticality }
        ]}
      />
    </>
  );
}
// Project version: VulnScope V1.5





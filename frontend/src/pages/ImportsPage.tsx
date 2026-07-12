import { FormEvent, useEffect, useState } from "react";
import { Upload } from "lucide-react";
import { api } from "../api/client";
import { DataTable } from "../components/DataTable";
import { Card, PageHeader } from "../components/Layout";

type ImportRecord = {
  id: string;
  source: string;
  status: string;
  asset_count: number;
  software_count: number;
  vulnerability_count: number;
  created_at: string;
};

const sample = JSON.stringify(
  {
    source: "defensive-import",
    assets: [
      {
        hostname: "web-01",
        ip_address: "10.0.0.10",
        os_name: "Ubuntu",
        os_version: "24.04",
        environment: "production",
        criticality: 4,
        software: [{ name: "openssl", version: "3.0.13", vendor: "OpenSSL", package_type: "deb" }]
      }
    ]
  },
  null,
  2
);

export function ImportsPage() {
  const [payload, setPayload] = useState(sample);
  const [imports, setImports] = useState<ImportRecord[]>([]);
  const [error, setError] = useState("");

  async function load() {
    setImports(await api.get<ImportRecord[]>("/imports"));
  }

  useEffect(() => {
    load();
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await api.post("/imports/scan-results", JSON.parse(payload));
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Import failed");
    }
  }

  return (
    <>
      <PageHeader title="Imports" />
      <Card className="mb-4">
        <form onSubmit={submit}>
          <textarea className="focus-ring h-72 w-full border border-line p-3 font-mono text-sm" value={payload} onChange={(e) => setPayload(e.target.value)} />
          {error && <div className="mt-3 border border-danger/30 bg-red-50 px-3 py-2 text-sm text-danger">{error}</div>}
          <button className="focus-ring mt-3 inline-flex items-center gap-2 bg-ink px-4 py-2 text-white"><Upload size={16} /> Import JSON</button>
        </form>
      </Card>
      <DataTable
        rows={imports}
        columns={[
          { key: "source", header: "Source", render: (row) => row.source },
          { key: "status", header: "Status", render: (row) => row.status },
          { key: "assets", header: "Assets", render: (row) => row.asset_count },
          { key: "software", header: "Software", render: (row) => row.software_count },
          { key: "created", header: "Created", render: (row) => new Date(row.created_at).toLocaleString() }
        ]}
      />
    </>
  );
}
// Project version: VulnScope V1.4

import { FormEvent, useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { api } from "../api/client";
import { DataTable } from "../components/DataTable";
import { Card, PageHeader } from "../components/Layout";
import { CVE } from "../types/models";

export function CvesPage() {
  const [cves, setCves] = useState<CVE[]>([]);
  const [cveId, setCveId] = useState("CVE-2026-0001");
  const [title, setTitle] = useState("OpenSSL package vulnerability");
  const [severity, setSeverity] = useState("high");
  const [cvssScore, setCvssScore] = useState(8.1);

  async function load() {
    setCves(await api.get<CVE[]>("/cves"));
  }

  useEffect(() => {
    load();
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    await api.post<CVE>("/cves", { cve_id: cveId, title, severity, cvss_score: cvssScore, description: title, references: [] });
    await load();
  }

  return (
    <>
      <PageHeader title="CVEs" />
      <Card className="mb-4">
        <form className="grid gap-3 lg:grid-cols-[160px_1fr_150px_120px_auto]" onSubmit={submit}>
          <input className="focus-ring border border-line px-3 py-2" value={cveId} onChange={(e) => setCveId(e.target.value)} />
          <input className="focus-ring border border-line px-3 py-2" value={title} onChange={(e) => setTitle(e.target.value)} />
          <select className="focus-ring border border-line px-3 py-2" value={severity} onChange={(e) => setSeverity(e.target.value)}>
            <option>critical</option>
            <option>high</option>
            <option>medium</option>
            <option>low</option>
          </select>
          <input className="focus-ring border border-line px-3 py-2" type="number" min={0} max={10} step={0.1} value={cvssScore} onChange={(e) => setCvssScore(Number(e.target.value))} />
          <button className="focus-ring inline-flex items-center justify-center gap-2 bg-ink px-4 py-2 text-white"><Plus size={16} /> Add</button>
        </form>
      </Card>
      <DataTable
        rows={cves}
        columns={[
          { key: "id", header: "CVE", render: (row) => row.cve_id },
          { key: "title", header: "Title", render: (row) => row.title },
          { key: "severity", header: "Severity", render: (row) => row.severity },
          { key: "score", header: "CVSS", render: (row) => row.cvss_score }
        ]}
      />
    </>
  );
}
// Project version: VulnScope V1.5






import { FormEvent, useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { api } from "../api/client";
import { DataTable } from "../components/DataTable";
import { Card, PageHeader } from "../components/Layout";
import { RemediationTask } from "../types/models";

export function RemediationPage() {
  const [tasks, setTasks] = useState<RemediationTask[]>([]);
  const [title, setTitle] = useState("Patch affected package");
  const [assignee, setAssignee] = useState("security-team");

  async function load() {
    setTasks(await api.get<RemediationTask[]>("/remediation-tasks"));
  }

  useEffect(() => {
    load();
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    await api.post<RemediationTask>("/remediation-tasks", { title, assignee, status: "todo" });
    await load();
  }

  async function update(id: string, status: string) {
    await api.patch(`/remediation-tasks/${id}`, { status });
    await load();
  }

  return (
    <>
      <PageHeader title="Remediation" />
      <Card className="mb-4">
        <form className="grid gap-3 md:grid-cols-[1fr_220px_auto]" onSubmit={submit}>
          <input className="focus-ring border border-line px-3 py-2" value={title} onChange={(e) => setTitle(e.target.value)} />
          <input className="focus-ring border border-line px-3 py-2" value={assignee} onChange={(e) => setAssignee(e.target.value)} />
          <button className="focus-ring inline-flex items-center justify-center gap-2 bg-ink px-4 py-2 text-white"><Plus size={16} /> Add</button>
        </form>
      </Card>
      <DataTable
        rows={tasks}
        columns={[
          { key: "title", header: "Title", render: (row) => row.title },
          { key: "assignee", header: "Assignee", render: (row) => row.assignee || "-" },
          { key: "status", header: "Status", render: (row) => row.status },
          {
            key: "update",
            header: "Update",
            render: (row) => (
              <select className="focus-ring border border-line px-2 py-1" value={row.status} onChange={(e) => update(row.id, e.target.value)}>
                <option value="todo">todo</option>
                <option value="in_progress">in_progress</option>
                <option value="done">done</option>
              </select>
            )
          }
        ]}
      />
    </>
  );
}
// Project version: VulnScope V1.5

